__author__ = 'anthony'
from util.db import log
import util.config as conf
import util.descr as descr
import util.recom as recom
import os,  sys,argparse
from datetime import datetime
import markdown


def fill_conf_var (db,user,port,host,passw):
    conf.BBDD = db
    conf.USERP =user
    conf.PORTP = port
    conf.SERVERP = host
    conf.PASS = passw

###main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pgrx',
                                     description='Script for get Descriptions, Recommendations and Descriptions about PostgreSQL database')
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', action='store', dest='action', required=True,
                        help='The action to execute by the app allowed values descr and recom')
    parser.add_argument('-U', action='store', dest='user',
                        help="User for connect to PostgreSQL, please prefer a super user (default: "+conf.USERP+")", default=conf.USERP)
    parser.add_argument('-d', action='store', dest='db',
                        help="Database to connect (default: "+conf.BBDD+")", default=conf.BBDD)
    parser.add_argument('-H', action='store', dest='host',
                        help="Host for connect to PostgreSQL (default: "+conf.SERVERP+")", default=conf.SERVERP)
    parser.add_argument('-p', action='store', dest='port',
                        help="Port for connect to PostgreSQL (default: "+conf.PORTP+")", default=conf.PORTP)
    parser.add_argument('-P', action='store', dest='passw',
                        help="Password for connect to PostgreSQL", default=conf.PASS)
    parser.add_argument('-o', action='store', dest='output',
                        help="Output format report values (md->markdown, html->html), (default: md)", default='md')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    #withot parameters, exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()

    if args.action =='descr':
        try:
            # stablish conf parameters to connextion
            fill_conf_var(args.db,args.user,args.port,args.host,args.passw)
            print "Obtaining information to describe for db " + conf.BBDD
            des = descr.descr()
            des.conex()
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
            ft = open("des_t1_.txt", "w+")
            ft.write(des.descr_version() + "\n")
            ft.write(des.descr_owner()+ "\n")
            ft.write(des.descr_uptime() + "\n")
            ft.write(des.descr_conf() + "\n")
            ft.write(des.descr_tbl()+ "\n")
            ft.write(des.descr_summary() + "\n")
            ft.write(des.descr_stat_db()+"\n")
            ft.write(des.descr_ext()+"\n")
            ft.write(des.descr_schema_per()+"\n")
            ft.write(des.descr_table_per() + "\n")
            ft.write(des.descr_top_size_tab()+"\n")
            ft.write(des.descr_top_used_tab()+"\n")
            ft.write(des.descr_top_used_index()+"\n")
            ft.write(des.descr_top_dead_tup_tab() + "\n")
            ft.write(des.descr_top_referenced_tab()+"\n")
            ft.write(des.descr_top_vaccum_tab() + "\n")
            ft.write(des.descr_latest_vaccum_tab()+ "\n")
            ft.close()

            f = open("des_t2_.txt", "w+")
            for t in des.toc:
                f.write(t + "\n")
            f.close()

            fr = open("des_" + conf.BBDD + "_" + dt_string + ".md", "w+")
            f = open("des_t2_.txt", "r")
            for x in f:
                fr.write(x)
            f = open("des_t1_.txt", "r")
            for x in f:
                fr.write(x)
            fr.close()
            os.remove("des_t2_.txt")
            os.remove("des_t1_.txt")
            if args.output=='html':
                html = markdown.markdownFromFile(input="des_" + conf.BBDD + "_" + dt_string + ".md",output="des_" + conf.BBDD + "_" + dt_string + ".html", extensions=['markdown.extensions.tables'])
                file = open("des_" + conf.BBDD + "_" + dt_string + ".html")
                contents = file.read()
                file.close()
                replaced_contents = contents.replace('<table>', '<table border=1>')
                os.remove("des_" + conf.BBDD + "_" + dt_string + ".html")
                file = open("des_" + conf.BBDD + "_" + dt_string + ".html","w+")
                file.write(replaced_contents)
                file.close()
                print "Information for Describe db in file " + "des_" + conf.BBDD + "_" + dt_string + ".html"
                os.remove("des_" + conf.BBDD + "_" + dt_string + ".md")
            else:
                print "Information for Describe db in file " + "des_" + conf.BBDD + "_" + dt_string + ".md"
            sys.exit()

        except ImportError, e:
            print "Error :", str(e)
            log.info(str(e))
            sys.exit()
        except KeyboardInterrupt:
            print " Bye ;-)"
            sys.exit()

    if args.action == 'recom':
        try:
            #stablish conf parameters to connextion
            fill_conf_var(args.db, args.user, args.port, args.host, args.passw)
            print "Obtaining information for recommendation for db "+conf.BBDD
            ###recommendations
            recom = recom.recom()
            recom.conex()
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
            ft = open("recom_t1_.txt", "w+")
            ft.write(recom.recom_conf_pg_hba()+"\n")
            ft.write(recom.recom_conf_shared_buffer()+"\n")
            ft.write(recom.recom_ddl_object_name_key_word()+"\n")
            ft.write(recom.recom_ddl_fk_without_index()+"\n")
            ft.write(recom.recom_ddl_index_unsued()+"\n")
            ft.write(recom.recom_ddl_index_invalid())
            ft.write(recom.recom_ddl_cero_one_column_table()+"\n")
            ft.write(recom.recom_ddl_table_without_pk()+"\n")
            ft.write(recom.recom_ddl_column_money()+"\n")
            ft.write(recom.recom_func_idle_in_trans()+"\n")
            ft.write(recom.recom_func_conex_vs_total_conex()+"\n")
            ft.write(recom.recom_func_table_bloat()+"\n")
            ft.write(recom.recom_func_index_bloat() + "\n")
            ft.write(recom.recom_func_frozen()+"\n")
            ft.write(recom.recom_ddl_compiletime_runtime_checks_plpgsql()+"\n")
            ft.close()

            f = open("recom_t2_.txt", "w+")
            for t in recom.toc:
                f.write(t+"\n")
            f.close()

            fr = open("recom_"+conf.BBDD+"_"+dt_string+".md", "w+")
            f = open("recom_t2_.txt", "r")
            for x in f:
                fr.write(x)
            f = open("recom_t1_.txt", "r")
            for x in f:
                fr.write(x)
            fr.close()
            os.remove("recom_t2_.txt")
            os.remove("recom_t1_.txt")
            if args.output=='html':
                html = markdown.markdownFromFile(input="recom_" + conf.BBDD + "_" + dt_string + ".md",
                                                 output="recom_" + conf.BBDD + "_" + dt_string + ".html",
                                                 extensions=['markdown.extensions.tables'])
                file = open("recom_" + conf.BBDD + "_" + dt_string + ".html")
                contents = file.read()
                file.close()
                replaced_contents = contents.replace('<table>', '<table border=1>')
                os.remove("recom_" + conf.BBDD + "_" + dt_string + ".html")
                file = open("recom_" + conf.BBDD + "_" + dt_string + ".html", "w+")
                file.write(replaced_contents)
                file.close()
                print "Information for Describe db in file " + "recom_" + conf.BBDD + "_" + dt_string + ".html"
                os.remove("recom_" + conf.BBDD + "_" + dt_string + ".md")
            else:
                print "Information for Recommendation in file "+"recom_"+conf.BBDD+"_"+dt_string+".md"
            sys.exit()

        except ImportError, e:
            print "Error :", str(e)
            log.info(str(e))
            sys.exit()
        except KeyboardInterrupt:
            print " Bye ;-)"
            sys.exit()

    print "Not allowed values for -a argument "
    parser.print_help()













