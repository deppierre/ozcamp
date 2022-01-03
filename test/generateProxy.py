import mdb, proxy

if __name__ == "__main__":    

    myProx = proxy.Proxy()
    myProx.insertNewIP()

    if len(myProx.proxy_list) > myProx.nb_proxy / 2:
        myMongodb = mdb.Mongodb()
        myMongodb.insertDropMany("proxy", myProx.proxy_list)
    else:
        print("FATAL error: not enough Proxy available")