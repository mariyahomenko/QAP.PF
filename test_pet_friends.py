from api import PetFriends  #берем из файла класс
from settings import valid_email, valid_password, invalid_email, invalid_password    #из другого файла - данные
import os   #встроенная управлялка файлами, нужна здесь для пикч

pf = PetFriends() #просто переименовываем

#ниже блок с простеньким тестом для валидного юзера
#типа получил ли он ответ кодом 200 + есть ли в результе кей
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)    #гет в файле api
    assert status == 200
    assert 'key' in result

#ниже то же, что и выше, но для невалидного юзера
#меняем название, вводим норм мыло и инвалидный пароль
def test_get_api_key_for_invalid_pass(email=valid_email, password=invalid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert result == 403

#а тут норм пароль, но инвалидное мыло, чтобы наверняка убедиться, что пропускаются только верные комбинации
#как и выше, проверяем, что юзер получит код из документации
def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert result == 403

#ниже опять этот гет, но для инвалидной пары
def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert result == 403



#ниже ф-ия для списка питомцев
#получаем ключ, запрашиваем список и проверяем, что ответ 200 и список не пустой
def test_get_all_pets_with_valid_key(filter=''):    #сейчас там доступен только 1 фильтр
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

#и ее функция-сестричка с инвалидными данными
#мы не получим статус, потому что мы не получим ключ, чтобы подставить его в get_list, поэтому криво ифаем
def test_get_all_pets_with_invalid_key(filter=''):
    _, auth_key = pf.get_api_key(invalid_email, invalid_password)
    if auth_key is not str:
        raise Exception("no")
    else:
        status, result = pf.get_list_of_pets(auth_key, filter)
        assert status == 403
        assert len(result['pets']) == 0



#добавление нового питомца
#в 1й строке задаем валидные данные, во 2й как-то так:
#имя = "я джойн и собираюсь поставить слеш между (получаем директорию до файла) и (имя файла)"
def test_add_new_pet_with_valid_data(name='Гриля', animal_type='двортерьер', age='4', pet_photo='images/4837_fullimage.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)   #получаем и обзываем ключ
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)    #добавляем всю инфу
    assert status == 200    #проверяем ответ от сервера, что все ок
    assert result['name'] == name   #и что хотя бы имя у нового питомца Гриля

#тоже добавление, но с некорректными данными
#насколько помню, там возраст от -1 до 4, пусть так
def test_add_new_pet_with_invalid_data(name='Гриля', animal_type='двортерьер', age='40', pet_photo='images/4837_fullimage.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400
    assert result['name'] != name   #проверяем откат, тип того



#вообще как-нибудь потом переделаю все портфолио на .эмодзи (будет хотя бы красиво, раз не круто с:)



#тестируем удаление
def test_successful_delete_self_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)   #гетим ключ
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #гетим список питомцев
    if len(my_pets['pets']) == 0:   #если длина джсона соответствует 0
        pf.add_new_pet(auth_key, "Скумби", "кот", '3', "images/w400h300.jpg") #то добавляем инфу о новом питомце
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #просим список питомцев, теперь уж не 0
    pet_id = my_pets['pets'][0]['id']   #обзываем айди, идем к джсону, берем первыЙ (0й) айди из списка
    status, _ = pf.delete_pet(auth_key, pet_id) #запрашиваем удаление
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #запрашиваем список питомцев
    assert status == 200
    assert pet_id not in my_pets.values()   #теперь удаленного айди не должно быть в списке

#тоже удаление, но несуществующего зверя, чтобы доказать или опровергнуть существование призраков
def test_unsuccessful_delete_self_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = 'ghost'  #тут мог бы быть ключ с индексами из брутфорса или тип того
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 403    #там нет ошибки на случай удаления несуществующего, но пусть так



#обновление инфы о питомце
#работает, если список не пуст, меняет первого зверя в списке
#иначе ругает
def test_successful_update_self_pet_info(name='ждвылжавыж', animal_type='кот', age='3'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")

#и негативное обновление
def test_unsuccessful_update_self_pet_info(name='ждвылжавыж', animal_type='длыдво', age='-3'):  #!
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400
        assert result['name'] != name
    else:
        raise Exception("There is no my pets")
#тест провалится и инфа обновится, хотя так быть не должно



#не хватает 3 тестов, поэтому ниже еще немного халтуры
def test_simple_add_new_pet_with_valid_data(name='Гриля', animal_type='двортерьер', age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

def test_simple_add_new_pet_with_unvalid_data(name='Гриля', animal_type='0', age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400
    assert result['name'] != name   #можно тип проверить, но вдруг добавится имя, а тип, например, будет пустым, - будет дырявая карточка



def test_add_photo_with_valid_data(pet_photo='images/w400h300.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)  #определяем фото
    _, auth_key = pf.get_api_key(valid_email, valid_password)   #получаем кей
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #получаем список зверей
    if len(my_pets['pets']) > 0:    #если больше нуля
        pet_id = my_pets['pets'][0]['id']   #то берем айди первого
        status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)   #добавляем фото
        assert status == 200
        assert result['pet_photo'] == pet_photo
    else:
        raise Exception("There is no my pets")  #иначе ругаемся

#дополнительная сестричка-простушка:
def test_add_photo_with_valid_data(pet_photo='blala.gif'): #или вообще .txt (хотя не знаю, имеет ли смысл)
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.add_photo_of_pet(auth_key, pet_id, pet_photo)
        assert status == 400    #или 403
        assert result['pet_photo'] != pet_photo
    else:
        raise Exception("There is no my pets")
