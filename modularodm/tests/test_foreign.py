
import unittest
from modularodm import StoredObject
from modularodm.fields.StringField import StringField
from modularodm.fields.IntegerField import IntegerField
from modularodm.fields.FloatField import FloatField
from modularodm.fields.BooleanField import BooleanField
from modularodm.fields.DateTimeField import DateTimeField
from modularodm.fields.ForeignField import ForeignField
from modularodm.storage.PickleStorage import PickleStorage
from modularodm.storage.MongoStorage import MongoStorage
from modularodm.validators import *
import random
import logging
import datetime
import os





class TestForeign(unittest.TestCase):

    def setUp(self):
        class Tag(StoredObject):
            value = StringField(primary=True)
            count = StringField(default='c', validate=True)
            misc = StringField(default='')
            misc2 = StringField(default='')
            created = DateTimeField(validate=True)
            modified = DateTimeField(validate=True, auto_now=True)
            keywords = StringField(default=['keywd1', 'keywd2'], validate=[MinLengthValidator(5), MaxLengthValidator(10)], list=True)
            mybool = BooleanField(default=False)
            myint = IntegerField()
            myfloat = FloatField(required=True, default=4.5)
            myurl = StringField(validate=URLValidator())


        class Blog(StoredObject):
            _id = StringField(primary=True, optimistic=True)
            body = StringField(default='blog body')
            title = StringField(default='asdfasdfasdf', validate=MinLengthValidator(8))
            tag = ForeignField('Tag', backref='tagged')
            tags = ForeignField('Tag', list=True, backref='taggeds')
            _meta = {'optimistic':True}

        Tag.set_storage(PickleStorage('tag'))
        Blog.set_storage(PickleStorage('blog'))

        self.tag1 = Tag(value=str(random.randint(0, 1000)), count='count_1', keywords=['keywd1', 'keywd3', 'keywd4'])
        self.tag1.save()

        self.tag2 = Tag(value=str(random.randint(0, 1000)), count="count_2", misc="foobar", misc2="a")
        self.tag2.save()

        self.tag3 = Tag(value=str(random.randint(0, 1000)), count="count_3", misc="foobaz", misc2="b")
        self.tag3.save()

        self.blog1 = Blog(title='blogtitle1')


    def test_for_ref(self):
        """
        test for foreign field reference
        """
        self.blog1.tag = self.tag2
        self.assertEqual(self.blog1.tag.count, "count_2")
        self.assertEqual(self.blog1.tag.misc, "foobar")
        self.assertEqual(self.blog1.tag.misc2, "a")

    def test_for_append(self):
        """
        test for append function
        """
        self.blog1.tags.append(self.tag2)
        self.blog1.tags.append(self.tag1)
        self.blog1.tags.append(self.tag3)
        self.assertTrue(self.blog1.tags[2] is self.tag3)

    def test_for_pop(self):
        """
        test for pop function
        """
        self.blog1.tags.append(self.tag2)
        self.blog1.tags.append(self.tag1)
        self.blog1.tags.append(self.tag3)
        self.tag6=self.blog1.tags.pop()
        self.assertTrue(self.tag6 is self.tag3)
        self.assertFalse(self.tag3 in self.blog1.tags)

    def test_for_set_item(self):
        """
        test for set_item function
        """
        self.blog1.tags.append(self.tag2)
        self.blog1.tags[0]=self.tag1
        self.assertTrue(self.tag1 in self.blog1.tags)
        self.assertFalse(self.tag2 in self.blog1.tags)

    def test_for_empty_tag(self):
        """
        test for empty function
        """
        self.blog1.tags.append(self.tag2)
        self.blog1.tags={}
        bool = self.tag2 in self.blog1.tags
        self.assertEqual(bool, False)


    def tearDown(self):
        try:os.remove('db_blog.pkl')
        except:pass
        try:os.remove('db_tag.pkl')
        except:pass

    # One-to-many tests


    # Many-to-many tests


# Run tests
if __name__ == '__main__':
    unittest.main()