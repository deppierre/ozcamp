import lib.mdb as mdb
import lib.proxy as proxy

if __name__ == "__main__":    

    myMongodb = mdb.Mongodb(database="ozcamp", collection="proxy")
    myMongodb.openNewConnection()

    myProx = proxy.Proxy()
    myProx.insertNewIPsFromFile("/Users/pdepretz/Documents/git/ozcamp/project/http_proxies.txt")

    if len(myProx.proxy_list) > myProx.nb_proxy / 2:
        myMongodb.insertDropMany(documents=myProx.proxy_list)
    else:
        print("FATAL error: not enough Proxy available.")