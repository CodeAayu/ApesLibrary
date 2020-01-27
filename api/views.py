from django.shortcuts import render
from api.models import localBooks
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import json, pandas as pd, requests

@csrf_exempt
def home(request):
	return render(request,'home.html',{"data":"haha"})

@csrf_exempt
def addbook(request):
	return render(request,'addbook.html',{"data":"haha"})

@csrf_exempt
def addtolocal(request):
	if request.user.is_authenticated:
		data = request.body
		data = json.loads(data)
		title = data["title"]
		authors = data["authors"]
		text = title + " " + authors
		link="https://www.googleapis.com/books/v1/volumes?q="+text+"&maxResults=1"
		req = requests.get(link)
		d = req.json()["items"][0]
		title = d["volumeInfo"]["title"]
		authors = d["volumeInfo"]["authors"]
		localBooks.objects.create(title=title, authors=authors, issued=False)
		return HttpResponse("Book added successfully")
	else:
		return HttpResponse("You are not Admin. Please login as admin.")

@csrf_exempt
def blahblah(request):
	#print(request.body)
	lala = request.body
	data = localBooks.objects.all().values()
	listing = list(data)
	return JsonResponse(listing, safe=False)

@csrf_exempt
def actualapi(request):
	data = request.body
	text = str(data)
	link="https://www.googleapis.com/books/v1/volumes?q="+text+"&maxResults=20"
	req = requests.get(link,headers={'Cache-Control': 'no-cache'})
	resl=req.json()['totalItems']
	if resl==0:
		df = pd.DataFrame({
		"title":["N.A"],
		"authors":["N.A"],
		"publishers":["N.A"],
		"publishedDate":["N.A"],
		"description":["N.A"],
		"thumbnails":["https://pngimage.net/wp-content/uploads/2018/06/image-not-available-png-8.png"],
		"categories":["N.A"],
		"previewLink":["http://www.fsxaddons.com/static/img/no-preview.jpg"],
		"pageCount":["N.A"],
		"language":["N.A"]
	})
	else:
		data = req.json()['items']
		titles = [item["volumeInfo"]['title'] if item["volumeInfo"].get('title') is not None else "Title not available" for item in data]
		all_authors = [[author for author in item['volumeInfo'].get('authors')] if item['volumeInfo'].get('authors') is not None else "Author not available" for item in data]
		publishers = [item['volumeInfo'].get('publisher') if item['volumeInfo'].get('publisher') is not None else "publisher not available" for item in data]
		publishedDate=[item['volumeInfo']['publishedDate'] if item['volumeInfo'].get('publishedDate') is not None else "published date not available" for item in data]
		description=[item['volumeInfo']['description'] if item['volumeInfo'].get('description') is not None else "description not available" for item in data]
		#thumbnails = [item['volumeInfo']['imageLinks']['thumbnail'] if item['volumeInfo'].get('imageLinks') is not None else "https://pngimage.net/wp-content/uploads/2018/06/image-not-available-png-8.png" for item in data]
		categories=  [[category for category in item['volumeInfo'].get('categories')] if item['volumeInfo'].get('categories') is not None else "category not available" for item in data]
		previewLink = [item['volumeInfo']['previewLink'] if item['volumeInfo'].get('previewLink') is not None else "http://www.fsxaddons.com/static/img/no-preview.jpg" for item in data]
		pageCount = [item['volumeInfo']['pageCount'] if item['volumeInfo'].get('pageCount') is not None else "Not Available" for item in data]
		language =[item['volumeInfo']['language'] if item['volumeInfo'].get('language') is not None else "Unknown" for item in data]
		exist =[]
		issued=[]
		for item in data:
			exs = localBooks.objects.filter(title=item["volumeInfo"]['title'])
			if exs.exists():
				exist.append(1)
				issued.append(exs[0].issued)
			else:
				exist.append(0)
				issued.append(-1)
		thumbnails=[]
		for item in data:
			slink = item["selfLink"]
			reqq=requests.get(slink)
			ourjsondata=reqq.json()
			if ourjsondata["volumeInfo"].get("imageLinks") is not None:
				if ourjsondata["volumeInfo"]["imageLinks"].get("medium") is not None:
					thumbnails.append(ourjsondata["volumeInfo"]["imageLinks"]["medium"])
				elif ourjsondata["volumeInfo"]["imageLinks"].get("small") is not None:
					thumbnails.append(ourjsondata["volumeInfo"]["imageLinks"]["small"])
				elif ourjsondata["volumeInfo"]["imageLinks"].get("thumbnail") is not None:
					thumbnails.append(ourjsondata["volumeInfo"]["imageLinks"]["thumbnail"])
			else:
				thumbnails.append("https://pngimage.net/wp-content/uploads/2018/06/image-not-available-png-8.png") 


		df = pd.DataFrame({
			"title":titles,
			"authors":all_authors,
			"publishers":publishers,
			"publishedDate":publishedDate,
			"description":description,
			"thumbnails":thumbnails,
			"categories":categories,
			"previewLink":previewLink,
			"pageCount":pageCount,
			"language":language,
			"exist":exist,
			"issued":issued
		})
	dfjson=json.loads(df.to_json(orient='records'))
	return JsonResponse(dfjson,safe=False)
