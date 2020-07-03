import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    insta_login = ''
    insta_pass = ""
    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['_kolpa__', '_dream_comes_true__', 'acheekyfox']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    followings_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.insta_login_link,
            method='POST',
            callback=self.my_page,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pass},
            headers={'x-csrftoken': csrf_token}
        )

    def my_page(self, response: HtmlResponse):
        json_body = json.loads(response.text)
        if json_body['authenticated']:
            for user in self.parse_users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_page,
                    cb_kwargs={'username': user}
                )

    def user_page(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'include_reel': True,
                     'fetch_mutual': False,
                     'first': 24}
        # сбор подписчиков
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.parse_user_followers,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )
        # сбор подписок
        url_followings = f'{self.graphql_url}query_hash={self.followings_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followings,
            callback=self.parse_user_followings,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )

    def parse_user_followers(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_followers,
                callback=self.parse_user_followers,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            yield InstaparserItem(
                user_name=username,
                user_id=user_id,
                follow_name=follower['node']['username'],
                follow_id=follower['node']['id'],
                follow_photo=follower['node']['profile_pic_url'],
                type_field='follower'
            )

    def parse_user_followings(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            url_followings = f'{self.graphql_url}query_hash={self.followings_hash}&{urlencode(variables)}'
            yield response.follow(
                url_followings,
                callback=self.parse_user_followings,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        followings = j_data.get('data').get('user').get('edge_follow').get('edges')
        for following in followings:
            yield InstaparserItem(
                user_name=username,
                user_id=user_id,
                type_field='following',
                follow_name=following['node']['username'],
                follow_id=following['node']['id'],
                follow_photo=following['node']['profile_pic_url']
            )

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')