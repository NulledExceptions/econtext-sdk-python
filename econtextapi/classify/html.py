# -*- coding: utf-8 -*-
from econtextapi.classify.classify import Classify

class Html(Classify):
    
    PATH = "/html"
    
    def __init__(self, client, classify_data=None, *args, **kwargs):
        super(Html, self).__init__(client, 'html', classify_data)
    
    def get_path(self):
        return "".join([super(Html, self).get_path(), Html.PATH])
    
    def process_result(self, response_object):
        """
        Provide scored_categories
        Provide scored_keywords
        """
        super(Html, self).process_result(response_object)
        self.scored_categories = response_object['scored_categories']
        self.scored_keywords = response_object['scored_keywords']
        self.title = response_object['title']
        return response_object
    
    def print_summary(self):
        print "Title: {}".format(self.title)
        print "Classifications:"
        for scored_category in self.scored_categories:
            print " * {:40} {:5}".format(self.categories[unicode(scored_category['category_id'])]['name'], scored_category['score'])
            
            
