from inspect import getcallargs
import json
import re
from unittest import result
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from bridgeBack import settings
import docx
from bridgeBack.utils.AuthToken import UserAuthToken
from textManage.models import TextCorpus
from textManage.serializers import TextsSerializer, AddTextSerializer, EditSerializer, FilesSerializer
import os
import uuid
from .models import File
from django.shortcuts import render, redirect
from win32com import client as wc
import pythoncom


class AllTextsView(APIView):
    authentication_classes = [UserAuthToken, ]

    def get(self, request):
        text_models = TextCorpus.objects.all()
        serializer = TextsSerializer(text_models, many=True)
        return Response({'status': 200, 'data': serializer.data})


class FileUploadView(APIView):
    authentication_classes = [UserAuthToken, ]

    def post(self, request):
        try:
            req = request.FILES.get('file')
            #  上传文件类型过滤
            file_type = re.match(r'.*\.(doc|docx)', req.name)
            if not file_type:
                return Response({'status': 401, 'msg': '文件不是word文件，请重新上传！'})
            filename = str(uuid.uuid1()) + req.name
            filepath = "{}\\upload\\".format(settings.BASE_DIR)
            writefile = open(
                os.path.join(filepath, filename), 'wb+')
            for chunk in req.chunks():  # 分块写入文件
                writefile.write(chunk)
                writefile.close()
            file_path = filepath + filename
            File.objects.create(
                filename=req.name, filepath=file_path, upload_method="post")
            return Response({'status': 200, 'msg': '上传成功！'})
        except Exception as e:
            print(e)
            return Response({'status': 401, 'msg': '服务器发生错误，请稍后重试'})


class FileGetView(APIView):
    authentication_classes = [UserAuthToken, ]

    def get(self, request):
        file_models = File.objects.all()
        serializer = FilesSerializer(file_models, many=True)
        return Response({'status': 200, 'data': serializer.data})


class FileDeleteView(APIView):
    authentication_classes = [UserAuthToken, ]

    def delete(self, request, pk):
        files = File.objects.get(id=pk)
        filename = files.filename
        if os.path.exists(files.filepath):
            os.remove(files.filepath)
        File.objects.filter(id=pk).delete()
        return Response({'status': 200, 'msg': '文件{}删除成功！'.format(filename)})


class GenTaskByFile(APIView):
    authentication_classes = [UserAuthToken, ]

    def post(self, request):
        data = request.data
        select_file = File.objects.get(id=data['id'])
        # py docx读取不了doc文件，需要做转换(不论后缀是不是docx，因为有的docx有可能是假的)
        tranfile = select_file.filepath
        if os.path.exists(select_file.filepath) == False:
            return Response({'status': 401, 'msg': '{}文件不存在，生成任务失败！请删除该条记录！'.format(select_file.filename)})
        tranDocToDocx(tranfile)
        # 提取word目录
        tranfile = select_file.filepath + "x"
        tmpfile = docx.Document(tranfile)
        result = catalogue_get(tmpfile)
        if(result == ""):
            if os.path.exists(tranfile):
                os.remove(tranfile)
            File.objects.filter(id=data['id']).delete()
            return Response({'status': 401, 'msg': '{}没有任何目录，将不会生成任务！将删除该文件！'.format(select_file.filename)})
        select_file.filepath = tranfile
        select_file.save()
        TextCorpus.objects.create(
            text_corpus_name=data['text_corpus_name'], text_corpus=result)
        return Response({'status': 200, 'msg': '生成任务成功！', 'filename': select_file.filename})


# Show file list


# Regular file upload without using ModelForm


# class AddTextView(APIView):
#
#     def post(self, request):
#         data = request.data
#         serializer = AddTextSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'status': 200, 'message': '新增成功'})
#         else:
#             return Response({'status': 400, 'message': serializer.errors['text_corpus_name'][0]})


# class DelTextView(APIView):
#
#     def post(self, request, pk):
#         TextCorpus.objects.filter(text_corpus_id=pk).delete()
#         return Response({'status': 200, 'message': '删除成功'})


# class EditTextView(APIView):
#
#     def post(self, request, pk):
#         try:
#             text_model = TextCorpus.objects.get(text_corpus_id=pk)
#             serializer = EditSerializer(instance=text_model, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({'status': 200, 'message': '修改成功'})
#             else:
#                 return Response({'status': 400, 'message': serializer.errors['non_field_errors'][0]})
#         except TextCorpus.DoesNotExist:
#             return Response({'status': 400, 'message': '数据不存在'})

# 转换doc为docx
def tranDocToDocx(tranfile):
    pythoncom.CoInitialize()
    word = wc.Dispatch("Word.Application")
    doc = word.Documents.Open(tranfile)
    doc.SaveAs("{}x".format(tranfile), 12)
    doc.Close()
    word.Quit()
    if os.path.exists(tranfile):
        os.remove(tranfile)

# 读取word中的目录


def catalogue_get(docs):
    lastest_heading = 0
    record = ['1']
    results = ""
    heading = ""
    headings = ""
    for paragraph in docs.paragraphs:
        print(paragraph.style.name, paragraph.text)
        if 'Heading' in paragraph.style.name:
            this_heading = int(paragraph.style.name[-1])
            if this_heading == 1 and lastest_heading == 0:
                heading = ''.join(record) + '.'
            else:
                if this_heading > lastest_heading:
                    record.append('1')
                elif this_heading == lastest_heading:
                    record[-1] = str(int(record[-1]) + 1)
                else:
                    record[this_heading -
                           1] = str(int(record[this_heading - 1]) + 1)
                    record[this_heading:] = []

            heading = '.'.join(record) + " "
            headings = '.'.join(record) + "| "
            if ("附录" in paragraph.text) & (paragraph.style.name == "Heading 2"):
                results = results + heading + \
                    paragraph.text.replace("\n", "") + \
                    paragraph.style.name + "\n"
            elif paragraph.style.name == "Heading 3":
                results = results + heading + paragraph.text + paragraph.style.name + "\n"
            elif paragraph.text != None:
                results = results + paragraph.text + paragraph.style.name + "\n"
            lastest_heading = this_heading
        elif ('Normal' in paragraph.style.name) | ('正文格式' in paragraph.style.name) | ('图标标题' in paragraph.style.name) | ('正文首行缩进' in paragraph.style.name):
            if (paragraph.text != None) & ('Heading' not in paragraph.style.name):
                results = results + headings + "日行占." + \
                    paragraph.text + paragraph.style.name + "\n"
    print(results)
    return results


class GetTextView(APIView):

    def get(self, request, pk):
        text_model = TextCorpus.objects.get(text_corpus_id=pk)
        serializer = TextsSerializer(text_model)
        return Response({'status': 200, 'data': serializer.data})
