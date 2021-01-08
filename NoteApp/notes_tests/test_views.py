from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Label, Notes
from django.urls import reverse
from rest_framework import status
import json


class TestNotesAPIs(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_1 = User.objects.create_user(username='birajit95',email='birajit95@gmail.com',password='123456')
        self.user_2 = User.objects.create_user(username='aryan75',email='aryan95@gmail.com',password='123456')


    def user_login(self, user=None):
        if user:
            username='birajit95'
        else:
            username = 'aryan75'
        self.valid_credential = json.dumps({
            'username':username,
            'password':'123456'
        })
        self.client.post(reverse('userLogin'), data=self.valid_credential, content_type='application/json')


    def userWiseLabelData(self, user_1_label=None, user_2_label=None):
        Label.objects.create(user=self.user_1, label_name=user_1_label)
        Label.objects.create(user=self.user_2, label_name=user_2_label)

    def addNote(self, title=None, content=None, label_name=None, user=None):
        label = Label.objects.create(user=user, label_name=label_name)
        note = Notes.objects.create(user=user, title=title,content=content)
        note.label.add(label)
        return note.id


    def test_add_label_when_user_is_logged_in(self, label_name='Google'):
        self.user_login(user='birajit95')
        label = json.dumps({
            'label_name':label_name
        })
        response = self.client.post(reverse('addLabel'), data=label, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['response_msg'], 'Label added')

    def test_add_label_when_user_is_not_logged_in(self, label_name='Facebook'):
        label = json.dumps({
            'label_name':label_name
        })
        response = self.client.post(reverse('addLabel'), data=label, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, '/user/login/?next=/notes/add-label/')

    def test_add_label_when_user_is_logged_in_and_given_blank_input(self, label_name=None):
        self.user_login(user='birajit95')
        label = json.dumps({
            'label_name':label_name
        })
        response = self.client.post(reverse('addLabel'), data=label, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_labels_when_user_is_loged_in_and_no_labels_found(self):
        self.user_login(user='birajit95')
        response = self.client.get(reverse('getLabels'))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_data'],'No labels found')

    def test_get_all_labels_when_user_is_not_loged_in(self):
        response = self.client.get(reverse('getLabels'))
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url,'/user/login/?next=/notes/get-labels/')

    def test_get_all_labels_when_user_is_loged_in_and_labels_found(self):
        self.user_login(user='birajit95')
        self.test_add_label_when_user_is_logged_in(label_name='Cat')
        self.test_add_label_when_user_is_logged_in(label_name='Dog')
        response = self.client.get(reverse('getLabels'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_delete_label_when_user_is_logged_in_and_label_is_found(self):
        self.test_add_label_when_user_is_logged_in(label_name="Cat")
        label_name = 'Cat'
        response = self.client.delete(reverse('deleteLabel',args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['response_msg'],'Label deleted')

    def test_delete_label_when_user_is_logged_in_and_label_is_not_found(self):
        self.test_add_label_when_user_is_logged_in(label_name="Cat")
        label_name = 'Dog'
        response = self.client.delete(reverse('deleteLabel',args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_msg'],f'{label_name} label is not exist')

    def test_delete_labels_when_user_is_not_loged_in(self):
        label_name = "Google"
        response = self.client.delete(reverse('deleteLabel', args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url,'/user/login/?next=/notes/delete-label/Google/')

    def test_delete_label_when_user_1_is_logged_in_and_tries_to_delete_user_2s_label(self):
        self.userWiseLabelData(user_1_label="Cat",user_2_label='Dog')
        self.user_login(user="birajit95")
        label_name = 'Dog'
        response = self.client.delete(reverse('deleteLabel',args=[label_name]))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_msg'],f'{label_name} label is not exist')

    def test_add_note_with_label_and_color_when_user_is_logged_in(self):
        self.test_add_label_when_user_is_logged_in(label_name="Google")
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'label': [{
                'label_name': 'Google'
            }],
            'color': '#FF5733'
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_without_label_and_color_when_user_is_logged_in(self):
        self.user_login()
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_without_label_but_with_color_when_user_is_logged_in(self):
        self.user_login()
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'color': '#FF5733'
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_with_label_but_without_color_when_user_is_logged_in(self):
        self.test_add_label_when_user_is_logged_in(label_name="Google")
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'label': [{
                'label_name': 'Google'
            }],
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_add_note_with_label_but_label_is_not_present_and_when_user_is_logged_in(self):
        self.userWiseLabelData(user_1_label="Google",user_2_label="Cat")
        self.user_login(user='birajit95')
        valid_payload_1 = {
            'title': 'Hello',
            'content': 'world',
            'label': [{
                'label_name': 'Cat'
            }],
        }
        response = self.client.post(reverse('addNote'),data=json.dumps(valid_payload_1), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(f"{response.data['response_msg']}",'Cat label is not exist')

    # test cases for note update

    def test_update_note_with_label_and_color_when_user_is_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.user_login(user=self.user_1)
        valid_payload_1 = {
            'title': 'Hello world',
            'content': 'Python',
            'label': [{
                'label_name': 'Google'
            }],
            'color': '#FF5733'
        }
        response = self.client.patch(reverse('updateNote', args=[note_id]), data=json.dumps(valid_payload_1),
                                    content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_update_note_with_label_and_without_color_when_user_is_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.userWiseLabelData(user_1_label="Dog", user_2_label='Cat')
        self.user_login(user=self.user_1)
        valid_payload_1 = {
            'title': 'Hello Brother',
            'content': 'Django',
            'label': [{
                'label_name': 'Dog'
            }]
        }
        response = self.client.patch(reverse('updateNote', args=[note_id]), data=json.dumps(valid_payload_1),
                                     content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_update_note_without_label_and_with_color_when_user_is_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.user_login(user=self.user_1)
        valid_payload_1 = {
            'title': 'Hello Brother',
            'content': 'Django',
            'color': '#FF5733'
        }
        response = self.client.patch(reverse('updateNote', args=[note_id]), data=json.dumps(valid_payload_1),
                                     content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_update_note_if_label_is_not_found_and_user_is_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.userWiseLabelData(user_1_label="Dog", user_2_label='Cat')
        self.user_login(user=self.user_1)
        valid_payload_1 = {
            'title': 'Hello Brother',
            'content': 'Django',
            'label': [{
                'label_name': 'Cat'
            }]
        }
        response = self.client.patch(reverse('updateNote', args=[note_id]), data=json.dumps(valid_payload_1),
                                     content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_note_if_note_id_is_not_found_and_user_is_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.userWiseLabelData(user_1_label="Dog", user_2_label='Cat')
        self.user_login(user=self.user_1)
        invalid_note_id=100
        valid_payload_1 = {
            'title': 'Hello Brother',
            'content': 'Django',
            'label': [{
                'label_name': 'Dog'
            }]
        }
        response = self.client.patch(reverse('updateNote', args=[invalid_note_id]), data=json.dumps(valid_payload_1),
                                     content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_note_without_label_and_color_when_user_is_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.user_login(user=self.user_1)
        valid_payload_1 = {
            'title': 'Hello Brother',
            'content': 'Django',
        }
        response = self.client.patch(reverse('updateNote', args=[note_id]), data=json.dumps(valid_payload_1),
                                     content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_update_note_when_user_is_not_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        valid_payload_1 = {
            'title': 'Hello Brother',
            'content': 'Django',
        }
        response = self.client.patch(reverse('updateNote', args=[note_id]), data=json.dumps(valid_payload_1),
                                     content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, f'/user/login/?next=/notes/update-note/{note_id}/')

    def test_delete_note_when_user_is_logged_in_and_when_note_is_not_trashsed(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.user_login(user=self.user_1)
        response = self.client.delete(reverse('deleteNote',args=[note_id]),content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['response_msg'], 'Your Note is trashed')

    def test_delete_note_when_user_is_logged_in_and_when_note_is_already_trashsed(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.user_login(user=self.user_1)
        self.client.delete(reverse('deleteNote',args=[note_id]),content_type='application/json')
        response = self.client.delete(reverse('deleteNote',args=[note_id]),content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['response_msg'], 'Your Note is deleted permanently')

    def test_delete_note_when_user_is_logged_in_but_note_is_not_present(self):
        self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        self.user_login(user=self.user_1)
        invalid_note_id = 100
        response = self.client.delete(reverse('deleteNote',args=[invalid_note_id]),content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_note_when_user_is_not_logged_in(self):
        note_id = self.addNote(title="Hello", content="World", label_name="Google", user=self.user_1)
        response = self.client.delete(reverse('deleteNote',args=[note_id]),content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, f'/user/login/?next=/notes/delete-note/{note_id}/')

    # Test cases for Note addition for specific label

    def test_add_note_for_given_label_when_user_is_logged_in(self):
        self.userWiseLabelData(user_1_label="Cat",user_2_label='Dog')
        self.user_login(user=self.user_1)
        label = 'Cat'
        valid_data = json.dumps({
            'title':'Hello',
            'content':'How are you?'
        })
        response = self.client.post(reverse('addNoteForLabel', args=[label]), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['response_msg'],'Your note is saved')

    def test_add_note_for_given_label_when_user_is_logged_in_and_color_is_given(self):
        self.userWiseLabelData(user_1_label="Cat",user_2_label='Dog')
        self.user_login(user=self.user_1)
        label = 'Cat'
        valid_data = json.dumps({
            'title':'Hello',
            'content':'How are you?',
            'color':'#FF5733'
        })
        response = self.client.post(reverse('addNoteForLabel', args=[label]), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['response_msg'],'Your note is saved')

    def test_add_note_for_given_label_when_user_is_logged_in_but_label_is_not_found(self):
        self.userWiseLabelData(user_1_label="Cat",user_2_label='Dog')
        self.user_login(user=self.user_1)
        label = 'Dog'
        valid_data = json.dumps({
            'title':'Hello',
            'content':'How are you?',
            'color':'#FF5733'
        })
        response = self.client.post(reverse('addNoteForLabel', args=[label]), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data['response_msg'],f'{label} label is not exist')


    def test_add_note_for_given_label_when_user_is_not_logged_in(self):
        self.userWiseLabelData(user_1_label="Cat",user_2_label='Dog')
        label = 'Dog'
        valid_data = json.dumps({
            'title':'Hello',
            'content':'How are you?',
            'color':'#FF5733'
        })
        response = self.client.post(reverse('addNoteForLabel', args=[label]), data=valid_data, content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, f'/user/login/?next=/notes/notes-for-label/{label}/')

    def test_get_notes_for_given_label_when_user_is_logged_in(self):
        self.addNote(title='Hello', content='world', label_name='Cat', user=self.user_1)
        self.user_login(user=self.user_1)
        label = 'Cat'
        response = self.client.get(reverse('addNoteForLabel', args=[label]), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_notes_for_given_label_when_user_is_not_logged_in(self):
        self.addNote(title='Hello', content='world', label_name='Cat', user=self.user_1)
        label = 'Cat'
        response = self.client.get(reverse('addNoteForLabel', args=[label]), content_type='application/json')
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, f'/user/login/?next=/notes/notes-for-label/{label}/')

    # Test cases for Trash and untrash APIs

    def test_get_trash_notes_when_user_is_logged_in_and_notes_are_available_in_trash(self):
        Notes.objects.create(title="Django",content="Hello Django", is_trash=True, user=self.user_1)
        self.user_login(user=self.user_1)
        response = self.client.get(reverse('trashNotes'))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_trash_notes_when_user_is_logged_in_and_notes_are_not_available_in_trash(self):
        self.user_login(user=self.user_1)
        response = self.client.get(reverse('trashNotes'))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_trash_notes_when_user_is_not_logged_in(self):
        Notes.objects.create(title="Django",content="Hello Django", is_trash=True, user=self.user_1)
        response = self.client.get(reverse('trashNotes'))
        self.assertEquals(response.status_code, status.HTTP_302_FOUND)
        self.assertEquals(response.url, f'/user/login/?next=/notes/trash/')


    def test_restore_trash_note_when_user_is_logged_in_and_valid_note_id_is_given(self):
       note = Notes.objects.create(title="Django", content="Hello Django", is_trash=True, user=self.user_1)
       self.user_login(user=self.user_1)
       response = self.client.patch(reverse('unTrashNotes',args=[note.id]))
       self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_restore_trash_note_when_user_is_logged_in_and_invalid_note_id_is_given(self):
       self.addNote(title="abc",content='ABC',label_name='Cat',user=self.user_1)
       self.user_login(user=self.user_1)
       note_id = 200
       response = self.client.patch(reverse('unTrashNotes',args=[note_id]))
       self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_restore_trash_note_when_user_is_not_logged_in(self):
       note_id = self.addNote(title="abc",content='ABC',label_name='Cat',user=self.user_1)
       response = self.client.patch(reverse('unTrashNotes',args=[note_id]))
       self.assertEquals(response.status_code, status.HTTP_302_FOUND)
       self.assertEquals(response.url, f'/user/login/?next=/notes/un-trash/{note_id}/')