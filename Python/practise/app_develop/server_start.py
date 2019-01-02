# -*- coding: utf-8 -*-
from flask import Flask, request, json
from flask.ext.restful import Api, Resource


# app继承Flask的类
app = Flask(__name__)
# api继承API和Flask的类
api = Api(app)


# 第一种方式：http://172.26.50.54:5000/jingqu?name=天台山
class JingQu(Resource):
    def get(self):
        args = request.args
        keywords = map(lambda x: x, args)
        from mongoDB import HandleDatabase
        handledatabase = HandleDatabase()
        # 用户查询景区时携带或者未携带GPS信息。
        if (len(keywords) == 1 and keywords[0] == "name") or (len(keywords) == 3 and sorted(["name", "longitude", "latitude"]) == sorted(keywords)):
            keyword = args.get("name")
            print type(keyword)
            print "scenic spot is " + keyword
            if "longitude" not in keywords:
                return handledatabase.get(keyword=keyword)
            else:
                return handledatabase.get(keyword=keyword, longitude=float(args.get("longitude")), latitude=float(args.get("latitude")))
        # 用户查询后选择的景区
        elif len(keywords) == 1 and keywords[0] == "jingqu_id":
            return handledatabase.get(jingqu_id=int(args.get("jingqu_id")))
        # 自助导游的时候自动获取最近的景点
        elif len(keywords) == 4 and sorted(["province", "city", "longitude", "latitude"]) == sorted(keywords):
            return handledatabase.get(province=args.get("province"), city = args.get("city"), longitude=float(args.get("longitude")), latitude=float(args.get("latitude")))

api.add_resource(JingQu, '/jingqu')
"""
# 第二种方式：http://172.26.50.54:5000/jingqu?name=天台山
@app.route('/jingqu', methods=['GET'])
def post():
    jinqu_keyword = request.args.get('name')
    print jinqu_keyword
    from mongoDB import HandleDatabase
    HandleDatabase = HandleDatabase()
    print HandleDatabase.get(jinqu_keyword)
    return str(HandleDatabase.get(jinqu_keyword))
"""
# socket for get scenic spot mapping.


class ScenicSpotMapping(Resource):
    def get(self):
        flag = False
        args = request.args
        keywords = map(lambda x: x, args)
        print keywords
        if len(keywords) == 0:
            flag = True
        elif "new" in keywords or "province" in keywords:
            flag = True
        if flag:
            import mongoDB
            handledatabase = mongoDB.HandleDatabase()
            return handledatabase.socket_jingqu_mapping(args=args)
        else:
            return {"status": "NOK"}
api.add_resource(ScenicSpotMapping, '/jingqu_mapping')


class ScenicSpotSpider(Resource):
    def get(self):
        args = request.args
        if sorted(map(lambda x: x, args)) == sorted(["jingqu_id", "label", "keyword", "description"]):
            from mongoDB import HandleDatabase
            handledatabase = HandleDatabase()
            if handledatabase.scenic_spot_spider(args=args):
                return {"status": "OK"}
            else:
                return {"status": "NOK"}
        else:
            print "args are wrong! and " + str(filter(lambda x: x not in map(lambda x: x, args), ["jingqu_id", "label", "keyword", "description"])) + " are missed!"
            print "args are wrong! and " + str(filter(lambda x: x not in ["jingqu_id", "label", "keyword", "description"], map(lambda x: x, args))) + " are more than defined!"
            return {"status": "NOK"}
api.add_resource(ScenicSpotSpider, '/jingqu_spider')


class JingdianSpider(Resource):
    def get(self):
        args = request.args
        # print filter(lambda x: x in ["id", "jingqu", "label", "keyword", "description"], map(lambda x: x, args))
        # print map(lambda x: x, args)
        if sorted(map(lambda x: x, args)) == sorted(["jingqu_id", "jingdian", "description"]):
            from mongoDB import HandleDatabase
            handledatabase = HandleDatabase()
            if handledatabase.jingdian_spider(args=args):
                return {"status": "OK"}
            else:
                return {"status": "NOK"}
        else:
            print "args are wrong! and " + str(filter(lambda x: x not in map(lambda x: x, args), ["jingqu_id", "jingdian", "description"])) + " are missed!"
            print "args are wrong! and " + str(filter(lambda x: x not in ["jingqu_id", "jingdian", "description"], map(lambda x: x, args))) + " are more than defined!"
            return {"status": "NOK"}

api.add_resource(JingdianSpider, '/jingdian_spider')

if __name__ == '__main__':
    app.run(host="172.26.50.54", debug=True)
