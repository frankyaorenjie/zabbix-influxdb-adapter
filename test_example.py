#!/usr/local/bin/python
# -*- coding:utf-8 -*-

import socket, os, sys, time, MySQLdb, traceback, string, random, fcntl, signal
#from angel_conf import *

error_log = '/tmp/angel.log'
# 定义读写语句
read_sql_conf = ('select')
write_sql_conf = ('delete', 'update', 'alter')
read_mysql_server = ()
write_mysql_server = ()
charset = 'utf8'
mysql_read_switch = mysql_write_switch = 0
cluster = {}


def pre_match_sql(data):
    return string.lower(data[:data.index(' ')].strip())


def seekreadmysql():
    random.seed()
    randmysqld = random.choice([i for i in range(len(read_mysql_server))])
    return read_mysql_server[randmysqld]


def seekwritemysql():
    return write_mysql_server


def strlen(strs):
    return len(str(strs))


def reap(signum, stackframe):
    '''''reap subfork'''
    while True:
        try:
            result = os.waitpid(-1, os.WNOHANG)
            if not result[0]: break
            print
            'reap child sucess %d' % result[0]
        except:
            break
    signal.signal(signal.SIGCHLD, reap)


def serialize(rows):
    sqltostr = '';
    i = 0;
    j = 1
    for row in rows:
        if j == 1:
            bracket = ''
        else:
            bracket = '}'
        sqltostr += '%si:%d;a:%d:{' % (bracket, j, len(row))
        j += 1
        for key in row:
            sqltostr += 's:%d:"%s";s:%d:"%s";' % (strlen(key), key, strlen(row[key]), row[key])
            i += 1
    heads = 'a:%d:{' % int(j - 1)
    sqltostr = heads + sqltostr + '}}'
    return sqltostr


class nettpl_content:
    def __init__(self, clientsk):
        self._clientsk = clientsk

    def myhandler(self, rcmysql):
        action = pre_match_sql(rcmysql)
        if not len(action):
            sys.exit(4)
            # allow read
        global mysql_read_switch;
        global mysql_write_switch;
        global cluster
        if action in read_sql_conf:
            try:
                if not mysql_read_switch:
                    rl = seekreadmysql()
                    cluster['readconn'] = MySQLdb.connect(host=rl['host'], user=rl['user'], passwd=rl['passwd'],
                                                          db=rl['database'])
                    mysql_read_switch = 1
            except MySQLdb.Error:
                print
                'mysql connect error'
                sys.exit(1)

            try:
                rdcursor = cluster['readconn'].cursor(MySQLdb.cursors.DictCursor)
                rdcursor.execute("SET NAMES %s" % charset)
                rdcursor.execute(rcmysql)
                rows = rdcursor.fetchall()
            except MySQLdb.Error:
                # errormsg = str(e.args[1])
                # self._clientsk.sendall(errormsg)
                # self.halt(rmsg)
                sys.exit(1)

            sqltostr = serialize(rows)
            self._clientsk.sendall(sqltostr)
            # self._clientsk.close()
            rdcursor.close()
        else:
            try:
                if not mysql_write_switch:
                    wl = seekwritemysql()
                    cluster['writecon'] = MySQLdb.connect(host=wl['host'], user=wl['user'], passwd=wl['passwd'],
                                                          db=wl['database'])
                    mysql_write_switch = 1
            except MySQLdb.Error:
                print
                'mysql connect error'
                sys.exit(1)
            print
            rcmysql
            wrcursor = cluster['writecon'].cursor()
            wrcursor.execute("SET NAMES %s" % charset)
            wrcursor.execute(rcmysql)
            wrcursor.close()

    def halt(self, errorcontent):
        hd = open(error_log, 'a+')
        fcntl.flock(hd, fcntl.LOCK_EX)
        hd.write('%s/t%s%s' % (errorcontent, time.ctime(), os.linesep))
        fcntl.flock(hd, fcntl.LOCK_UN)
        hd.close()


class nettpl:
    '''''forking network model'''

    def __init__(self, host, port):
        self.__host = host
        self.__port = port

    def server(self):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.bind((self.__host, self.__port))
        sk.listen(1)
        global mysql_switch

        while True:
            try:
                clientsk, clientaddr = sk.accept()
                print(clientsk, clientaddr)
            except socket.error:
                continue
            except KeyboardInterrupt:
                print
                "[yhm]angel stop"
                sys.exit(4)
            signal.signal(signal.SIGCHLD, reap)

            father = os.fork()
            if father:
                clientsk.close()
                continue
            else:
                sk.close()
                try:
                    while True:
                        clientdata = clientsk.recv(4096)
                        if not len(clientdata): break
                        # callback class

                        myhandler = nettpl_content(clientsk)
                        myhandler.myhandler(clientdata)
                        # except:
                        # traceback.print_exc()
                finally:
                    print
                    'complete its work'
                    sys.exit(1)


network = nettpl('localhost', 9009)  # 端口默认定义是9009
network.server()
