__author__ = 'anthony'
###recom zone
recom_conf_pg_hba = """ SELECT line_number, type, database,user_name,case when address is null then '' else address end ,case when netmask is null then '' else netmask end  ,
                                    auth_method, case when  options is null then array[''] else options end , case when error is null then '' else error end FROM pg_hba_file_rules WHERE auth_method = 'trust' """

recom_func_conex_vs_total_conex = """SELECT  (sum(numbackends)*100)/  current_setting('max_connections')::int   FROM pg_stat_database"""

recom_conf_shared_buffer = """SELECT  blks_hit * 100 / (blks_read + blks_hit) as BUFFER FROM pg_stat_database where datname=current_database() and blks_read + blks_hit<>0;"""

recom_func_idle_in_trans = """select pid,client_addr,query,now()-state_change  from pg_stat_activity  where state = 'idle in transaction' and now()-state_change>'_$1_'"""

recom_ddl_object_name_key_word = """ SELECT column_name, string_agg (table_name,',') FROM information_schema.columns  WHERE table_schema not in ('information_schema','pg_catalog') and column_name in (select word from pg_get_keywords()) group by 1"""

recom_ddl_table_without_pk = """select tbl.table_schema, tbl.table_name from information_schema.tables tbl
        where table_type = 'BASE TABLE'   and table_schema not in ('pg_catalog', 'information_schema')
        and not exists (select 1  from information_schema.key_column_usage kcu    where kcu.table_name = tbl.table_name  and kcu.table_schema = tbl.table_schema)"""

recom_ddl_fk_without_index = """SELECT c.conrelid::regclass AS tab, string_agg(a.attname, ',' ORDER BY x.n) AS col, c.conname AS const,
                   c.confrelid::regclass AS referenced_tab FROM pg_catalog.pg_constraint c    CROSS JOIN LATERAL
                  unnest(c.conkey) WITH ORDINALITY AS x(attnum, n)   JOIN pg_catalog.pg_attribute a  ON a.attnum = x.attnum
                     AND a.attrelid = c.conrelid WHERE NOT EXISTS 
             (SELECT 1 FROM pg_catalog.pg_index i   WHERE i.indrelid = c.conrelid  AND (i.indkey::smallint[])[0:cardinality(c.conkey)-1]@> c.conkey) 
              AND c.contype = 'f' GROUP BY c.conrelid, c.conname, c.confrelid ORDER BY pg_catalog.pg_relation_size(c.conrelid) DESC;"""

recom_ddl_index_unsued = """SELECT    schemaname || '.' || relname    tab, indexrelname FROM pg_stat_user_indexes WHERE idx_scan = 0 """

recom_ddl_index_invalid = """SELECT n.nspname, c.relname FROM   pg_catalog.pg_class c, pg_catalog.pg_namespace n,  pg_catalog.pg_index i WHERE  (i.indisvalid = false OR i.indisready = false) AND
                                            i.indexrelid = c.oid AND c.relnamespace = n.oid AND     n.nspname != 'pg_catalog' AND   n.nspname != 'information_schema' AND   n.nspname != 'pg_toast' """

recom_ddl_cero_one_column_table = """SELECT  table_schema||'.'||table_name tab, count(column_name) col FROM information_schema.columns  WHERE table_schema not in ('information_schema','pg_catalog') group by 1 having count(column_name)=1 
                                    union all 
                                    select  table_schema||'.'||table_name tab, 0  from  information_schema.tables  where table_schema not in ('information_schema','pg_catalog') and  table_schema||'.'||table_name  not in (select table_schema||'.'||table_name FROM information_schema.columns)"""

recom_ddl_column_money = """select  table_schema||'.'||table_name tab, column_name from information_schema.columns WHERE table_schema not in ('information_schema','pg_catalog') and data_type='money'"""

recom_func_table_bloat = """with sub as (SELECT schemaname, tblname, bs*tblpages AS real_size,
              (tblpages-est_tblpages)*bs AS extra_size,
              CASE WHEN tblpages - est_tblpages > 0
                THEN 100 * (tblpages - est_tblpages)/tblpages::float
                ELSE 0
              END AS extra_ratio, fillfactor, (tblpages-est_tblpages_ff)*bs AS bloat_size,
              CASE WHEN tblpages - est_tblpages_ff > 0
                THEN 100 * (tblpages - est_tblpages_ff)/tblpages::float
                ELSE 0
              END AS bloat_ratio, is_na
              -- , (pst).free_percent + (pst).dead_tuple_percent AS real_frag
            FROM (
              SELECT ceil( reltuples / ( (bs-page_hdr)/tpl_size ) ) + ceil( toasttuples / 4 ) AS est_tblpages,
                ceil( reltuples / ( (bs-page_hdr)*fillfactor/(tpl_size*100) ) ) + ceil( toasttuples / 4 ) AS est_tblpages_ff,
                tblpages, fillfactor, bs, tblid, schemaname, tblname, heappages, toastpages, is_na
                -- , stattuple.pgstattuple(tblid) AS pst
              FROM (
                SELECT
                  ( 4 + tpl_hdr_size + tpl_data_size + (2*ma)
                    - CASE WHEN tpl_hdr_size%ma = 0 THEN ma ELSE tpl_hdr_size%ma END
                    - CASE WHEN ceil(tpl_data_size)::int%ma = 0 THEN ma ELSE ceil(tpl_data_size)::int%ma END
                  ) AS tpl_size, bs - page_hdr AS size_per_block, (heappages + toastpages) AS tblpages, heappages,
                  toastpages, reltuples, toasttuples, bs, page_hdr, tblid, schemaname, tblname, fillfactor, is_na
                FROM (
                  SELECT
                    tbl.oid AS tblid, ns.nspname AS schemaname, tbl.relname AS tblname, tbl.reltuples,
                    tbl.relpages AS heappages, coalesce(toast.relpages, 0) AS toastpages,
                    coalesce(toast.reltuples, 0) AS toasttuples,
                    coalesce(substring(
                      array_to_string(tbl.reloptions, ' ')
                      FROM '%fillfactor=#"__#"%' FOR '#')::smallint, 100) AS fillfactor,
                    current_setting('block_size')::numeric AS bs,
                    CASE WHEN version()~'mingw32' OR version()~'64-bit|x86_64|ppc64|ia64|amd64' THEN 8 ELSE 4 END AS ma,
                    24 AS page_hdr,
                    23 + CASE WHEN MAX(coalesce(null_frac,0)) > 0 THEN ( 7 + count(*) ) / 8 ELSE 0::int END
                     AS tpl_hdr_size,
                    sum( (1-coalesce(s.null_frac, 0)) * coalesce(s.avg_width, 1024) ) AS tpl_data_size,
                    bool_or(att.atttypid = 'pg_catalog.name'::regtype)
                      OR count(att.attname) <> count(s.attname) AS is_na
                  FROM pg_attribute AS att
                    JOIN pg_class AS tbl ON att.attrelid = tbl.oid
                    JOIN pg_namespace AS ns ON ns.oid = tbl.relnamespace
                    LEFT JOIN pg_stats AS s ON s.schemaname=ns.nspname
                      AND s.tablename = tbl.relname AND s.inherited=false AND s.attname=att.attname
                    LEFT JOIN pg_class AS toast ON tbl.reltoastrelid = toast.oid
                  WHERE att.attnum > 0 AND NOT att.attisdropped
                    AND tbl.relkind = 'r'
                  GROUP BY 1,2,3,4,5,6,7,8,9,10
                  ORDER BY 2,3
                ) AS s
              ) AS s2
            ) AS s3)
            select schemaname||'.'||tblname tab,round(extra_ratio::numeric,2) from sub where extra_ratio>30 order by 2 desc """

recom_func_index_bloat = """with sub as (
        SELECT current_database(), nspname AS schemaname, tblname, idxname, bs*(relpages)::bigint AS real_size,
          bs*(relpages-est_pages)::bigint AS extra_size,
          100 * (relpages-est_pages)::float / relpages AS extra_ratio,
          fillfactor,
          CASE WHEN relpages > est_pages_ff
            THEN bs*(relpages-est_pages_ff)
            ELSE 0
          END AS bloat_size,
          100 * (relpages-est_pages_ff)::float / relpages AS bloat_ratio,
          is_na
          -- , 100-(pst).avg_leaf_density AS pst_avg_bloat, est_pages, index_tuple_hdr_bm, maxalign, pagehdr, nulldatawidth, nulldatahdrwidth, reltuples, relpages -- (DEBUG INFO)
        FROM (
          SELECT coalesce(1 +
                 ceil(reltuples/floor((bs-pageopqdata-pagehdr)/(4+nulldatahdrwidth)::float)), 0 -- ItemIdData size + computed avg size of a tuple (nulldatahdrwidth)
              ) AS est_pages,
              coalesce(1 +
                 ceil(reltuples/floor((bs-pageopqdata-pagehdr)*fillfactor/(100*(4+nulldatahdrwidth)::float))), 0
              ) AS est_pages_ff,
              bs, nspname, tblname, idxname, relpages, fillfactor, is_na
              -- , pgstatindex(idxoid) AS pst, index_tuple_hdr_bm, maxalign, pagehdr, nulldatawidth, nulldatahdrwidth, reltuples -- (DEBUG INFO)
          FROM (
              SELECT maxalign, bs, nspname, tblname, idxname, reltuples, relpages, idxoid, fillfactor,
                    ( index_tuple_hdr_bm +
                        maxalign - CASE -- Add padding to the index tuple header to align on MAXALIGN
                          WHEN index_tuple_hdr_bm%maxalign = 0 THEN maxalign
                          ELSE index_tuple_hdr_bm%maxalign
                        END
                      + nulldatawidth + maxalign - CASE -- Add padding to the data to align on MAXALIGN
                          WHEN nulldatawidth = 0 THEN 0
                          WHEN nulldatawidth::integer%maxalign = 0 THEN maxalign
                          ELSE nulldatawidth::integer%maxalign
                        END
                    )::numeric AS nulldatahdrwidth, pagehdr, pageopqdata, is_na
                    -- , index_tuple_hdr_bm, nulldatawidth -- (DEBUG INFO)
              FROM (
                  SELECT n.nspname, i.tblname, i.idxname, i.reltuples, i.relpages,
                      i.idxoid, i.fillfactor, current_setting('block_size')::numeric AS bs,
                      CASE -- MAXALIGN: 4 on 32bits, 8 on 64bits (and mingw32 ?)
                        WHEN version() ~ 'mingw32' OR version() ~ '64-bit|x86_64|ppc64|ia64|amd64' THEN 8
                        ELSE 4
                      END AS maxalign,
                      /* per page header, fixed size: 20 for 7.X, 24 for others */
                      24 AS pagehdr,
                      /* per page btree opaque data */
                      16 AS pageopqdata,
                      /* per tuple header: add IndexAttributeBitMapData if some cols are null-able */
                      CASE WHEN max(coalesce(s.null_frac,0)) = 0
                          THEN 2 -- IndexTupleData size
                          ELSE 2 + (( 32 + 8 - 1 ) / 8) -- IndexTupleData size + IndexAttributeBitMapData size ( max num filed per index + 8 - 1 /8)
                      END AS index_tuple_hdr_bm,
                      /* data len: we remove null values save space using it fractionnal part from stats */
                      sum( (1-coalesce(s.null_frac, 0)) * coalesce(s.avg_width, 1024)) AS nulldatawidth,
                      max( CASE WHEN i.atttypid = 'pg_catalog.name'::regtype THEN 1 ELSE 0 END ) > 0 AS is_na
                  FROM (
                      SELECT ct.relname AS tblname, ct.relnamespace, ic.idxname, ic.attpos, ic.indkey, ic.indkey[ic.attpos], ic.reltuples, ic.relpages, ic.tbloid, ic.idxoid, ic.fillfactor,
                          coalesce(a1.attnum, a2.attnum) AS attnum, coalesce(a1.attname, a2.attname) AS attname, coalesce(a1.atttypid, a2.atttypid) AS atttypid,
                          CASE WHEN a1.attnum IS NULL
                          THEN ic.idxname
                          ELSE ct.relname
                          END AS attrelname
                      FROM (
                          SELECT idxname, reltuples, relpages, tbloid, idxoid, fillfactor, indkey,
                              pg_catalog.generate_series(1,indnatts) AS attpos
                          FROM (
                              SELECT ci.relname AS idxname, ci.reltuples, ci.relpages, i.indrelid AS tbloid,
                                  i.indexrelid AS idxoid,
                                  coalesce(substring(
                                      array_to_string(ci.reloptions, ' ')
                                      from 'fillfactor=([0-9]+)')::smallint, 90) AS fillfactor,
                                  i.indnatts,
                                  pg_catalog.string_to_array(pg_catalog.textin(
                                      pg_catalog.int2vectorout(i.indkey)),' ')::int[] AS indkey
                              FROM pg_catalog.pg_index i
                              JOIN pg_catalog.pg_class ci ON ci.oid = i.indexrelid
                              WHERE ci.relam=(SELECT oid FROM pg_am WHERE amname = 'btree')
                              AND ci.relpages > 0
                          ) AS idx_data
                      ) AS ic
                      JOIN pg_catalog.pg_class ct ON ct.oid = ic.tbloid
                      LEFT JOIN pg_catalog.pg_attribute a1 ON
                          ic.indkey[ic.attpos] <> 0
                          AND a1.attrelid = ic.tbloid
                          AND a1.attnum = ic.indkey[ic.attpos]
                      LEFT JOIN pg_catalog.pg_attribute a2 ON
                          ic.indkey[ic.attpos] = 0
                          AND a2.attrelid = ic.idxoid
                          AND a2.attnum = ic.attpos
                    ) i
                    JOIN pg_catalog.pg_namespace n ON n.oid = i.relnamespace
                    JOIN pg_catalog.pg_stats s ON s.schemaname = n.nspname
                                              AND s.tablename = i.attrelname
                                              AND s.attname = i.attname
                    GROUP BY 1,2,3,4,5,6,7,8,9,10,11
              ) AS rows_data_stats
          ) AS rows_hdr_pdg_stats
        ) AS relation_stats
        ORDER BY nspname, tblname, idxname)
        
        select schemaname, tblname||'->'||idxname, pg_size_pretty (real_size) size , round( bloat_ratio::numeric,2)  from sub 
        where bloat_ratio>30 and   schemaname not in  ('pg_catalog','information_schema')
        ;"""

recom_func_frozen = """select round(((age(datfrozenxid)::numeric*100)/current_setting('autovacuum_freeze_max_age')::numeric ),4) from pg_database where datname = current_database()"""

recom_ddl_compiletime_runtime_checks_plpgsql = """SELECT nm.nspname||'.'||proname, pg_get_functiondef(pr.oid)
                FROM pg_proc pr join  pg_type tp on (tp.oid = pr.prorettype) join pg_language l  on (pr.prolang=l.oid)  left join pg_stat_user_functions pgst on (pr.oid = pgst.funcid) join pg_namespace nm on ( pr.pronamespace = nm.oid)
                WHERE  l.lanname='plpgsql'  and pr.pronamespace IN (  SELECT oid    FROM pg_namespace  WHERE nspname NOT LIKE 'pg_%'  AND nspname != 'information_schema'  )"""

recom_ddl_compiletime_runtime_checks_plpgsql_2 = """select string_agg(nspname,',') from pg_namespace where nspname not like 'pg_%'  and nspname <>'information_schema';"""


###descr zone
descr_uptime = """SELECT now() - pg_postmaster_start_time() as UPTIME,pg_postmaster_start_time() as UPTIME_from, now() -pg_conf_load_time() TIME_CONF,pg_conf_load_time() as CONF_from  ;"""

descr_conf = """select name, current_setting(name) from pg_settings  where name = 'log_line_prefix' or
        name = 'log_statement' or name = 'log_connections' or name = 'log_disconnections' or
        name = 'archive_mode' or name='archive_command'  or name = 'listen_addresses' or
        name = 'search_path' or name='shared_preload_libraries' or name='password_encryption' or name = 'log_checkpoints' or name='log_min_duration_statement' 
        or name = 'work_mem' or name='shared_buffers'  or name='show maintenance_work_mem' or name ='effective_cache_size'
        or name = 'autovacuum' or name='autovacuum_analyze_scale_factor'  or name='show autovacuum_vacuum_scale_factor' or name ='autovacuum_max_workers'
        or name = 'autovacuum_naptime' or name='autovacuum_vacuum_cost_delay'  or name='show autovacuum_vacuum_cost_limit' or name ='max_connections' or name ='max_wal_size'"""

descr_owner = """select usename from pg_catalog.pg_database join pg_catalog.pg_user on (datdba=usesysid) where datname=current_database()"""

descr_tbl = """SELECT spcname,round(  (pg_tablespace_size(spcname)/1024)/1024,2) tamanoMB , pg_tablespace_location(oid) as ubicacion FROM pg_tablespace;"""

descr_summary = """SELECT ns.nspname||'.'|| pg.relname as name , reltuples::int ,round((pg_relation_size(psat.relid::regclass)/1024)/1024::numeric,2)::text || ' MB' as Weigth,round((pg_total_relation_size(psat.relid::regclass)/1024)/1024::numeric,2)::text || ' MB' as Weigth_total,n_live_tup,n_dead_tup,
                 psat.seq_scan,psat.seq_tup_read,COALESCE( psat.idx_scan,0) as index_scan , COALESCE( psat.idx_tup_fetch,0) as index_fetch,n_tup_ins,n_tup_del,n_tup_upd FROM pg_class pg JOIN pg_stat_user_tables psat ON (pg.relname = psat.relname)
                join pg_namespace a on ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid)
                   ORDER BY 2 DESC   ;
                   (SELECT ns.nspname as schema ,(select count (*)  from pg_tables where schemaname=ns.nspname) as cantidad_tablas,
                    (select count(*) from pg_indexes where schemaname=ns.nspname) as cantidad_indices,
                    (select count (*)  from pg_catalog.pg_views where schemaname NOT IN ('pg_catalog', 'information_schema') and schemaname=ns.nspname) as cantidad_vistas,
                    (SELECT count(*) FROM pg_proc pr join  pg_type tp on (tp.oid = pr.prorettype)   left join pg_stat_user_functions pgst on (pr.oid  = pgst.funcid) join pg_namespace nm on ( pr.pronamespace= nm.oid) WHERE    pr.pronamespace IN (  SELECT oid    FROM pg_namespace  WHERE nspname NOT LIKE 'pg_%'  AND nspname !='information_schema' AND nspname=ns.nspname) ) as cantidad_funciones,
                    (select  count(*) from information_schema.triggers where trigger_schema=ns.nspname) as cantidad_triggers,
                    COALESCE(sum (round((pg_relation_size(psat.relid::regclass)/1024)/1024::numeric,2)::real),0 )as peso_tabla,
                    COALESCE( sum( round((pg_indexes_size(psat.relid::regclass)/1024)/1024::numeric,2)::real),0) AS peso_index
                    FROM pg_class pg JOIN pg_stat_user_tables psat ON (pg.relname = psat.relname)
                                    join pg_namespace a on ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid)
                                    left join pg_stat_user_indexes AS idstat ON idstat.relname = psat.relname
                                      group by 1  ORDER BY 2 DESC   )"""

descr_stat_db = """SELECT  numbackends as CONN, xact_commit as TX_COMM,
              xact_rollback as TX_RLBCK, 
              round((blks_hit * 100)::numeric / nullif((blks_read + blks_hit),0),2)::text ||'%' as BUFFER , 
              round((tup_fetched *100)::numeric/nullif((tup_fetched + tup_inserted+tup_updated+tup_deleted),0),2)::text ||'%' as tup_fetched ,
              round((tup_inserted *100)::numeric/nullif((tup_fetched + tup_inserted+tup_updated+tup_deleted),0),2)::text ||'%' as tup_inserted,
              round((tup_updated *100)::numeric/nullif((tup_fetched + tup_inserted+tup_updated+tup_deleted),0),2)::text ||'%' as tup_updated,
              round((tup_deleted *100)::numeric/nullif((tup_fetched + tup_inserted+tup_updated+tup_deleted),0),2)::text ||'%' as tup_deleted,
               temp_files, deadlocks, conflicts,
             stats_reset
             FROM pg_stat_database where datname=current_database()"""

descr_ext = """select string_agg(extname,',') from pg_extension """

descr_schema_per = """select nspname,pg_catalog.pg_get_userbyid(nspowner) ,coalesce(replace (replace (nspacl::text,'{',''),'}','' ),'')from pg_namespace where nspname not like 'pg_%'  and nspname <>'information_schema';  """

descr_table_per = """select grantee usr,table_schema||'.'||table_name as tab, string_agg(privilege_type,',') perm from information_schema.table_privileges where table_schema<> 'pg_catalog' and table_schema<>'information_schema'   group by 1,2 order by 1;"""

descr_top_referenced_tab = """with sub as (
                        SELECT
                        tc.constraint_name, 
                        tc.table_name, 
                        kcu.column_name, 
                        ccu.table_schema AS foreign_table_schema,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                          AND tc.table_schema = kcu.table_schema
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                          AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    order by 5) 
                    select foreign_table_name "table", count(*) count_of_fk_to_table, string_agg(table_name,',') tables_with_fk_to_table from sub 
                    group by 1 order by 2 desc limit 5 """

descr_top_size_tab = """SELECT ns.nspname||'.'|| pg.relname as name , round((pg_relation_size(psat.relid::regclass)/1024)/1024::numeric,2) Weigth FROM pg_class pg JOIN 
		 pg_stat_user_tables psat ON (pg.relname = psat.relname)
		join pg_namespace a on ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid) order by 2 desc limit 5"""

descr_top_used_tab = """SELECT ns.nspname||'.'|| pg.relname as name ,COALESCE (psat.seq_scan,0)+COALESCE( psat.idx_scan,0) as used_times FROM pg_class pg JOIN pg_stat_user_tables psat ON (pg.relname = psat.relname)
            join pg_namespace a on ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid)
               ORDER BY 2 DESC  limit 5"""

descr_top_used_index = """SELECT idstat.schemaname,idstat.relname ||'->'||indexrelname AS index_name,idstat.idx_scan AS times_used,  round((pg_relation_size(idstat.indexrelid::regclass)/1024)/1024::numeric)::text || ' MB' AS index_size
                FROM pg_stat_user_indexes AS idstat  JOIN pg_stat_user_tables AS tabstat ON idstat.relname = tabstat.relname  ORDER BY 3 desc limit 5"""

descr_top_dead_tup_tab = """SELECT ns.nspname||'.'|| pg.relname as name , n_dead_tup  FROM pg_class pg JOIN  pg_stat_user_tables psat ON (pg.relname = psat.relname)
		join pg_namespace a on ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid) order by 2 desc limit 5"""

descr_top_vaccum_tab = """SELECT ns.nspname||'.'|| pg.relname as name ,  autovacuum_count,COALESCE( to_char(last_autovacuum,'YYYY:MM:DD-HH24:MI:SS'),'-') as fecha_last_auto,vacuum_count,
                COALESCE(to_char(last_vacuum,'YYYY:MM:DD-HH24:MI:SS'),'-' ) as fecha_last_vac   FROM pg_class pg JOIN pg_stat_user_tables psat ON (pg.relname = psat.relname)  join pg_namespace a on
                 ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid) ORDER BY 2 DESC limit 5;"""

descr_latest_vaccum_tab =""" SELECT ns.nspname||'.'|| pg.relname as name ,
      case
        when last_autovacuum > coalesce(last_vacuum, '0001-01-01') then last_autovacuum::timestamp(0)::text
        when last_vacuum is not null then last_vacuum::timestamp(0)::text
        else '-'
      end as "last_vacuumed",
      case
        when last_autovacuum > coalesce(last_vacuum, '0001-01-01') then 'autovacuum'
        when last_vacuum is not null then 'manual'
        else '-'
      end as "vacuum type"
              FROM pg_class pg JOIN pg_stat_user_tables psat ON (pg.relname = psat.relname)  join pg_namespace a on
                 ( pg.relnamespace = a.oid)  join pg_namespace ns  on (pg.relnamespace = ns.oid) ORDER BY 2  desc nulls last limit 5;"""