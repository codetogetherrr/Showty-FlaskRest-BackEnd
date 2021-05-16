from flask_restful import Resource, reqparse
from models.user import UserModel
from schemas.user import UserSchema, UserUpdateSchema
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from flask import make_response, render_template, request
from marshmallow import ValidationError
from datetime import timedelta
from werkzeug.security import generate_password_hash
import requests
import os
import re

user_schema = UserSchema()
user_update_schema = UserUpdateSchema(many=True)


class UserFacebookRegisterLogin(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('facebook_access_token', type=str, required=True, help="This field cannot be left blank!")

    def get_facebook_profile_data(self, facebook_access_token: str):
        headers = {'Content-Type': 'application/json'}
        payload = {'fields': 'email, name', 'access_token': facebook_access_token}
        url = 'https://graph.facebook.com/me'
        profileDataResponse = requests.get(url, headers=headers, params=payload)
        return profileDataResponse

    def get_facebook_profile_pic(self, height: int, width: int, facebook_access_token: str):
        headers = {'Content-Type': 'application/json'}
        payload = {'redirect': 'false', 'height': height, 'width': width, 'access_token': facebook_access_token}
        url = 'https://graph.facebook.com/me/picture'
        profilePicResponse = requests.get(url, headers=headers, params=payload)
        return profilePicResponse

    def upload_pic_cloudinary(self, url: str, upload_preset: str, cloud_name: str):
        headers = {'Content-Type': 'application/json'}
        payload = {'upload_preset': upload_preset, 'file': url}
        url = 'https://api.cloudinary.com/v1_1/' + cloud_name + '/image/upload'
        cloudinaryPicUploadResponse = requests.get(url, headers=headers, params=payload)
        return cloudinaryPicUploadResponse

    def post(self):
        data = UserFacebookRegisterLogin.parser.parse_args()
        profileDataResponse = self.get_facebook_profile_data(data['facebook_access_token'])
        
        if profileDataResponse.status_code == 200:
            profileData = profileDataResponse.json()
            if UserModel.find_by_email(profileData['email']):
                newData = {}
                if UserModel.find_by_email(profileData['email']).fullname == "":
                    newData['fullname'] = profileData['name']
                if UserModel.find_by_email(profileData['email']).image_id == "":
                    profilePicResponse = self.get_facebook_profile_pic(320,320,data['facebook_access_token'])
                    if profilePicResponse.status_code == 200:
                        profilePicData = profilePicResponse.json()
                        profilePicUrl = profilePicData['data']['url']
                        upload_preset = os.environ.get('CLOUDINARY_UPLOAD_PRESET', '')
                        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
                        cloudinaryPicUploadResponse = self.upload_pic_cloudinary(profilePicUrl, upload_preset, cloud_name)
                        if cloudinaryPicUploadResponse.status_code == 200:
                            cloudinaryPicUploadData = cloudinaryPicUploadResponse.json()
                            newData['image_id'] = cloudinaryPicUploadData['public_id']
                            newData['image_height'] = cloudinaryPicUploadData['height']
                            newData['image_width'] = cloudinaryPicUploadData['width']
                        else:
                            errorData = cloudinaryPicUploadResponse.json()
                            print("errorhere1")
                            return errorData, cloudinaryPicUploadResponse.status_code    

                    elif profilePicResponse.status_code == 400:
                        errorData = profilePicResponse.json()
                        if errorData['error']['code'] == 190:
                            print("errorhere3")
                            return {'message': errorData['error']['message']}, 401
                    else:
                        responseData = profilePicResponse.json()
                        print("errorhere2")
                        return responseData, profilePicResponse.status_code
                    
                if not newData:
                    login = UserModel.find_by_email(profileData['email']).login
                    return {'tokens': {'access_token': create_access_token(identity=login,expires_delta=timedelta(seconds=120)), 'refresh_token': create_refresh_token(identity=login)}, 'mergeable': False}, 200
                else:
                    login = UserModel.find_by_email(profileData['email']).login
                    return {'user': newData, 'tokens': {'access_token': create_access_token(identity=login,expires_delta=timedelta(seconds=120)), 'refresh_token': create_refresh_token(identity=login)}, 'mergeable': True}, 200
                    
            else:
                
                profilePicResponse = self.get_facebook_profile_pic(320,320,data['facebook_access_token'])
                if profilePicResponse.status_code == 200:
                    profilePicData = profilePicResponse.json()
                    profilePicUrl = profilePicData['data']['url']
                    upload_preset = os.environ.get('CLOUDINARY_UPLOAD_PRESET', '')
                    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
                    cloudinaryPicUploadResponse = self.upload_pic_cloudinary(profilePicUrl, upload_preset, cloud_name)
                    if cloudinaryPicUploadResponse.status_code == 200:
                        cloudinaryPicUploadData = cloudinaryPicUploadResponse.json()
                            
                        possibleLogin = profileData['email'].split("@")[0]
                        fullname = profileData['name']
                        finalLogin = self.generateLogin(possibleLogin)
                        email = profileData['email']
                        image_id = cloudinaryPicUploadData['public_id']
                        image_height = cloudinaryPicUploadData['height']
                        image_width = cloudinaryPicUploadData['width']
                        
                        user=UserModel(finalLogin, "", fullname, email, "", "", "", image_id, image_height, image_width)
                        user.activated = True
                        user.save_to_db()
                        
                        return {'tokens':{'access_token': create_access_token(identity=finalLogin,expires_delta=timedelta(seconds=120)), 'refresh_token': create_refresh_token(identity=finalLogin)}, 'mergeable': False}, 200
                        
                    else:
                        errorData = cloudinaryPicUploadResponse.json()
                        print("errorhere4")
                        return errorData, cloudinaryPicUploadResponse.status_code    

                elif profilePicResponse.status_code == 400:
                    errorData = profilePicResponse.json()
                    if errorData['error']['code'] == 190:
                        print("errorhere5")
                        return {'message': errorData['error']['message']}, 401
                else:
                    responseData = profilePicResponse.json()
                    print("errorhere6")
                    return responseData, profilePicResponse.status_code
                
        elif profileDataResponse.status_code == 400:
            errorData = profileDataResponse.json()
            if errorData['error']['code'] == 190:
                print("errorhere6")
                return {'message': errorData['error']['message']}, 401
        else:
            responseData = profileDataResponse.json()
            print("errorhere7")
            return responseData, profileDataResponse.status_code

    def generateLogin(self, login):

        logins = UserModel.list_all_logins()

        if login in logins:

            if re.findall('\d{1,}', login):
                preLogin = login[:len(login) - len(str(re.findall('\d{1,}', login)[-1]))]
                numericEndsFinal = [re.findall('\d{1,}',u) for u in logins if u[:len(u) - len(re.findall('\d{1,}',u)[-1])] == preLogin]
                iter = min([int(a[-1]) for a in numericEndsFinal if [str(int(a[0]) + 1)] not in numericEndsFinal]) + 1
            else:
                preLogin = login
                iter = 1

        return preLogin + str(iter)

class CurrentUser(Resource):

    @jwt_required
    def get(self):
        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            return user_schema.dump(user), 200
        else:
            return {"message": "User not found"}, 404


class User(Resource):

    def post(self):

        try:
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.login):
            return {"message": "User with that login already exists."}, 200
        if UserModel.find_by_email(user.email):
            return {"message": "Email is already in use."}, 200

        user.password = generate_password_hash(user.password)

        user.save_to_db()
        #user.send_conf_email()
        return {"message": "User created successfully. Activation link sent to email provided"}, 201


    @jwt_required
    def get(self, user_login):
        login = get_jwt_identity()
        user=UserModel.find_by_username(login)
        if user:
            user_to_return = UserModel.find_by_username(user_login)
            if user_to_return:
                return user_schema.dump(user_to_return), 200
            else:
                {"message": "User not found"}, 404
        else:
            return {"message":"User not found"}, 404

    @jwt_required
    def put(self):
        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            try:
                user_to_update = user_update_schema.load(request.get_json(), partial=True, instance=user)
            except ValidationError as err:
                return err.messages, 400
            user_to_update.save_to_db()
            return {"message": "User profile updated successfully"}, 200
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def delete(self):
        login = get_jwt_identity()
        user=UserModel.find_by_username(login)
        if user:
            user.delete_from_db()
            return {"message": "User deleted"}, 200
        else:
            return {"message": "User not found"}, 404


class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id:int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        user.activated = True
        user.save_to_db()
        #return redirect("http://localhost:3000", code=302)
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=user.email), 200, headers)


class Users(Resource):
    @jwt_required
    def get(self):
        return {'users': [user_schema.dump(x) for x in UserModel.query.all()]}

