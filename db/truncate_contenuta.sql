SET AUTOCOMMIT = 0;
START TRANSACTION;

truncate table maadb_project.emoji_contenuta;
truncate table maadb_project.emoticon_contenuta;
truncate table maadb_project.hashtag_contenuto;
truncate table maadb_project.parola_contenuta;
truncate table maadb_project.parola;

commit;