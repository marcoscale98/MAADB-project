# Cose da fare
Convertire liste in set e dizionari nel preprocessing
1. fare aggregazione dati su MongoDB
2. fare aggregazione dati su python per MySQL
3. creare MySQL db per buffer e statistiche
4. creare db con statistiche
5. visualizzare db con statistiche
6. fare più istanze di MongoDB

## ottimizzazione preprocessing
### baseline
18145 ms per 30 tweet
### con pipe spacy ottimization
15150 ms per 30 tweet
### più si aumentano i tweet e meno la faccenda è drammatica
 37473 ms per 3000 tweet
458000 ms per 60000 tweets

## ottimizzazione upload_words
2869 secondi per 60000 tweets

## con ottimizzazione di upload_words
473 s per 60000 tweets
11 s per 60000 tweets
