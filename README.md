
pgrx
-------------------------

pgrx is an app to generate reports in markdown/HTML format about some recommendations and can obtain general descriptions from  Postgres database, this app uses some mix queries from the postgres catalog that can help to detect some possible problem and anomalies related to database performance, design and security.



Requirements and Usage
-------------------------

**Requirements**

* App and lib:

   1-:    python 2.x
   
   2-:    python (psycopg2,markdown)
   
   3-:    Tested whit 10+ (with previous versions can execute but are not yet tested )
   



* The following OS are supported:
  1- Linux (modern RHEL/CentOS or Debian/Ubuntu; others are not yet tested);


**Usage**

Example of Use

Download from  https://github.com/asotolongo/pgrx

```
cd pgrx
python pgrx.py --help
usage: pgrx [-h] -a ACTION [-U USER] [-d DB] [-H HOST] [-p PORT] [-P PASSW]
            [-o OUTPUT] [--version]

Script for get Descriptions, Recommendations and Descriptions about PostgreSQL
database

optional arguments:
  -h, --help  show this help message and exit
  -U USER     User for connect to PostgreSQL, please prefer a super user
              (default: postgres)
  -d DB       Database to connect (default: postgres)
  -H HOST     Host for connect to PostgreSQL (default: localhost)
  -p PORT     Port for connect to PostgreSQL (default: 5432)
  -P PASSW    Password for connect to PostgreSQL
  -o OUTPUT   Output format report values (md->markdown, html->html),
              (default: md)
  --version   show program's version number and exit

required named arguments:
  -a ACTION   The action to execute by the app allowed values descr and recom






```



Get  recommendations from a database 

```
python pgrx.py -a recom -d dell_test -H localhost -U postgres -P password

Obtaining information for recommendation for db dell_test
Information for recommendation in file recom_dell_test_2019-12-26_11-08-09.md
```

Get  descriptions from a database 

```
python pgrx.py -a descr -d dell_test -H localhost -U postgres -P password

Obtaining information to describe for db dell_test
Information for Describe db in file des_dell_test_2019-12-26_11-10-21.md

```


**Docker**

- Enter to docker folder:
 cd docker
- Build the docker image:
docker build -t my-pgrx .
- Test pgrx:
docker run -it --rm --name my-pgrx-app my-pgrx
- Run pgrx:
docker run -it --rm --name my-pgrx-app -v "$PWD":/app my-pgrx python pgrx.py -a recom -H IP -d your_database -P yourpass -o html


**IMPORTANT:** 
If There're bugs in the existing version or if you have some suggestion please contact to me.  

Anthony R. Sotolongo leon
asotolongo@gmail.com
