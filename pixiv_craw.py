import requests
from bs4 import BeautifulSoup
import sys,os
import json

#BeautifulSoup(markup, "lxml")

class pixiv_lib(object):
    def __init__(self):
        self.__session=requests.Session()
        self.__session.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.125 Safari/537.36'})
        self.__depth=0
        self.__max_depth=20
        self.__max_pics=300
        self.__pics=0
        if not os.path.exists('pixiv_images'):
            os.makedirs('pixiv_images')
        self.__dir_name=''
        self.__readed=[]
        self.__commder=7



    def config(self,session_id,max_depth=20,max_pics=300,dir_name='pixiv_images'):
        self.__max_depth=max_depth
        self.__dir_name=dir_name
        self.__save_dir='pixiv_images/'+self.__dir_name+'/'
        if not os.path.exists('pixiv_images'):
            os.makedirs(os.getcwd()+'/pixiv_images/'+self.__dir_name)
        self.__cookies={"PHPSESSID":session_id}
        self.__session.cookies.update(self.__cookies)



    def __download_page_pic(self,url,ref):
        file_name=self.__save_dir+url.split('/')[-1]
        if not os.path.exists(file_name):
            try:
                img=self.__session.get(url,headers={"Referer":ref})
            except Exception:
                print('Connect failure,Retring......')
                self.__download_page_pic(url,ref)
                return

            if(img.status_code!=200):
                print('Download Error!')
                print(img.text)
                return

            fd=open(file_name,"wb")
            for chunk in img.iter_content():
                fd.write(chunk)
            fd.close()
            self.__pics+=1
            if(self.__pics>self.__max_pics):
            	print('Get Max Pics Exit')
            	sys.exit()
            return



    def __get_manga(self,url,ref):
    	try:
    		page=self.__session.get(url,headers={'Referer':ref})
    	except Exception:
    		print("Get page failure,Retring...")
    		self.__get_manga(url,ref)
    		return

    	if(page.status_code!=200):
    		print("Get Page Error")
    		return

    	soup=BeautifulSoup(page.text)
    	pics=soup.find_all('div',class_='item-container')
    	for i in pics:
    		pic_url=i.img['src']
    		self.__download_page_pic(pic_url,url)

    	return




    def recursion_craw(self,url,ref='http://www.pixiv.net'):
        self.__depth+=1
        print('Enter url: '+url)
        if(self.__depth>self.__max_depth):
            self.__depth-=1
            return

        try:
            page=self.__session.get(url,headers={'Referer':ref})
        except Exception:
            print("Get page failure,Retring...")
            self.__depth-=1
            self.recursion_craw(url,ref)
            return

        if(page.status_code!=200):
            print("Get Page Error!")
            self.__depth-=1
            return

        pic_id=url.split('=')[-1]
        self.__readed.append(int(pic_id))
        soup=BeautifulSoup(page.text)

        if soup.find('div',class_='works_display')==None:
        	self.__max_depth-=1
        	print('Not have pics')
        	return

        if soup.find('div',class_='works_display').find('a')==None:
        	img_url=soup.find_all('div',class_='wrapper')[1].img['data-src']
        	self.__download_page_pic(img_url,url);
        else:
        	manga_url='http://www.pixiv.net/'+soup.find('div',class_='works_display').a['href']
        	self.__get_manga(manga_url,url)

        pic_recomd=self.get_recomd(ref,pic_id)

        i=0
        for pics in pic_recomd:
            if pics not in self.__readed:
                self.recursion_craw('http://www.pixiv.net/member_illust.php?mode=medium&illust_id='+str(pics),url)
            i+=1
            if i>=self.__commder:
            	break
        self.__depth-=1
        if(self.__depth==0):
        	print("Max Depth Exit")
        return



    def get_recomd(self,ref,pic_id):
        try:
        	recv_data=self.__session.get('http://www.pixiv.net/rpc/recommender.php?rand=324&type=illust&sample_illusts='+pic_id+'&num_recommendations=100',headers={'Referer':ref});
        except Exception:
        	print("Get recommender error,Retring...")
        	return self.get_recomd(ref,pic_id)

        if(recv_data.status_code!=200):
            print("Get recommender error!")
            return []

        return json.loads(recv_data.text)['recommendations']



def main():
	pixiv=pixiv_lib()
	max_depth=int(raw_input('put max depth(recursion): '))
	max_pics=int(raw_input('put max pics: '))
	session=raw_input('put the PHPSESSID: ')
	dir_name=raw_input('put the save dir name: ')
	pixiv.config(session,max_depth,max_pics,dir_name)
	start_url=raw_input('put the start url: ')
	pixiv.recursion_craw(start_url)

main()
