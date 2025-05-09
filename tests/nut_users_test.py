# -*- coding: utf-8 -*-
import os
from importlib import reload
import unittest

from pyfakefs.fake_filesystem_unittest import TestCase

from nut import Users

_DEFAULT_USER = 'guest'
_DEFAULT_PASSWORD = 'guest'
_DEFAULT_HOST = 'localhost'

class NutUsersTest(TestCase):
	"""Tests for nut/Users.py
	"""
	def setUp(self):
		self.setUpPyfakefs()

	def test_first_user(self):
		first_user = Users.first()
		self.assertEqual(first_user.id, _DEFAULT_USER)
		self.assertEqual(first_user.password, _DEFAULT_PASSWORD)
		Users.users = {}
		self.assertIsNone(Users.first())

	def test_auth_positive(self):
		auth_result = Users.auth(_DEFAULT_USER, _DEFAULT_PASSWORD, _DEFAULT_HOST)
		self.assertEqual(auth_result.id, _DEFAULT_USER)
		self.assertEqual(auth_result.password, _DEFAULT_PASSWORD)

		self.assertEqual(Users.first().remoteAddr, None)
		self.assertIsNotNone(Users.auth(_DEFAULT_USER, _DEFAULT_PASSWORD, 'any_adrr'))

		user = Users.first()
		user.setRequireAuth(False)
		user.remoteAddr = _DEFAULT_HOST
		Users.users[user.id] = user
		self.assertTrue(Users.auth(user.id, user.password, user.remoteAddr))

		user.setRequireAuth(True)
		self.assertTrue(Users.auth(_DEFAULT_USER, _DEFAULT_PASSWORD, user.remoteAddr))
		self.assertFalse(Users.auth(_DEFAULT_USER, _DEFAULT_PASSWORD, 'any_addr'))

	def test_auth_negative(self):
		self.assertEqual(Users.auth(_DEFAULT_USER, 'wrong_pwd', _DEFAULT_HOST), None)
		self.assertEqual(Users.auth('wrong_user', _DEFAULT_PASSWORD, _DEFAULT_HOST), None)

	def test_list_default_users(self):
		reload(Users)
		values = Users.users.values()
		self.assertIsNotNone(values)
		self.assertGreater(len(values), 0)

	def test_export(self):
		FILENAME = 'conf/users.conf'
		self.assertFalse(os.path.exists(FILENAME))
		Users.export()
		self.assertTrue(os.path.exists(FILENAME))

	def test_user_serialize(self):
		user = Users.first()
		serialized = user.serialize()
		self.assertEqual(serialized, "guest|guest")

	def test_user_load_csv(self):
		user = Users.User()
		USER = 'user1'
		PASSWORD = 'password1'
		csv = f'{USER}|{PASSWORD}'
		user.loadCsv(csv, map=['id', 'password'])
		self.assertEqual(user.id, USER)
		self.assertEqual(user.password, PASSWORD)

	def test_user_load_csv_with_empty_map(self):
		user = Users.User()
		user.loadCsv("id|pwd")
		self.assertIsNone(user.id)
		self.assertIsNone(user.password)

	def test_load_with_empty_file(self):
		Users.users = {}
		Users.load()

		self.assertIsNotNone(Users.first())
		first_user = Users.first()
		self.assertEqual(first_user.id, _DEFAULT_USER)
		self.assertEqual(first_user.password, _DEFAULT_PASSWORD)

	def test_load(self):
		conf_file = 'conf/users.conf'
		conf_content = """id|password
user1|pwd1

user2|pwd2
# comment
user3|pwd3
"""
		self.fs.create_file(conf_file, contents=conf_content)

		Users.users = {}
		Users.load()

		self.assertIsNotNone(Users.first())
		first_user = Users.first()
		self.assertEqual(first_user.id, 'user1')
		self.assertEqual(first_user.password, 'pwd1')

		self.fs.remove(conf_file)

	def test_user_set_switch_port(self):
		user = Users.User()
		self.assertEqual(user.switchPort, None)
		new_switch_port = 1234
		user.setSwitchPort(new_switch_port)
		self.assertEqual(user.switchPort, new_switch_port)

		user.setSwitchPort('wrong_port')
		self.assertEqual(user.switchPort, new_switch_port)

	def test_user_get_switch_port(self):
		user = Users.User()
		new_switch_port = 1234
		user.setSwitchPort(new_switch_port)
		self.assertEqual(user.getSwitchPort(), new_switch_port)

		user.setSwitchPort('wrong_port')
		self.assertEqual(user.switchPort, new_switch_port)

	def test_user_set_switch_host(self):
		user = Users.User()
		self.assertEqual(user.switchHost, None)
		new_switch_host = 'local'
		user.setSwitchHost(new_switch_host)
		self.assertEqual(user.switchHost, new_switch_host)

	def test_user_get_switch_host(self):
		user = Users.User()
		new_switch_host = 'local'
		user.setSwitchHost(new_switch_host)
		self.assertEqual(user.getSwitchHost(), new_switch_host)

	def test_user_set_require_auth(self):
		user = Users.User()
		self.assertTrue(user.requireAuth)
		user.setRequireAuth(False)
		self.assertFalse(user.requireAuth)
		user.setRequireAuth(True)
		user.setRequireAuth('incorrect')
		self.assertTrue(user.requireAuth)
		user.setRequireAuth(False)
		user.setRequireAuth('incorrect')
		self.assertFalse(user.requireAuth)

	def test_user_set_is_admin(self):
		user = Users.User()
		self.assertFalse(user.isAdmin)
		user.setIsAdmin(True)
		self.assertTrue(user.isAdmin)
		user.setIsAdmin(False)
		user.setIsAdmin('incorrect')
		self.assertFalse(user.isAdmin)
		user.setIsAdmin(True)
		user.setIsAdmin('incorrect')
		self.assertTrue(user.isAdmin)

	def test_user_get_require_auth(self):
		user = Users.User()
		self.assertIs(user.getRequireAuth(), str(True), 'All users require Auth by default')
		user.setRequireAuth(False)
		self.assertIs(user.getRequireAuth(), str(False))

if __name__ == "__main__":
	unittest.main()
