# MAADB-project
Progetto d'esame per MAADB
## Versione di Python
Python 3.9
## Schema di lavoro
[Descrizione progetto](https://docs.google.com/document/d/1i3TSJpyr4vw-edKBX1XNuy52f8_Sem0aPWmo6fBpuBs/edit?ts=57308c63#heading=h.oublcismo327)
### Cosa c'è da creare?
#### Pipeline di preprocessing dei tweets

##### Oggetto di output
````
{
  int: {
    "id":i,
    "frase_ripulita": str,
    "hashtags":list(str),
    "emoticons":list(str),
    "emojis":list(str),
    'parole': list(
      {
        token: str,
        lemma: str,
        pos: str,
      }
    )
  }
}
````
es.
````
{
  0:{
    'id': 0, 
    'frase_ripulita': " f u what's that spell ? fired up ? noo  haha \n",
     'hashtags': ['#fuckyou'],
      'emoticons': [], 
      'emojis': [],
       'parole': [{'token': "'s", 'lemma': 'be', 'pos': 'VERB'},{'token': 'spell', 'lemma': 'spell', 'pos': 'NOUN'}, {'token': 'fired', 'lemma': 'fire', 'pos': 'VERB'}, {'token': 'noo', 'lemma': 'noo', 'pos': 'VERB'}, {'token': 'haha', 'lemma': 'haha', 'pos': 'NOUN'}]
  },
  1: {
    'id': 1,
     'frase_ripulita': "now all of you roll tide bandwagon fans will hop off alabama's dick . one wor d: overrated . \n", 
     'hashtags': [],
      'emoticons': [], 
      'emojis': [],
       'parole': [{'token': 'roll', 'lemma': 'roll', 'pos': 'VERB'}, {'token': 'tide', 'lemma': 'tide', 'pos': 'NOUN'}, {'token': 'bandwagon', 'lemma': 'bandwagon', 'pos': 'NOUN'}, {'token': 'fans', 'lemma': 'fan', 'pos': 'NOUN'}, {'token': 'hop', 'lemma': 'hop', 'pos': 'VERB'}, {'token': 'alabama', 'lemma': 'alabama', 'pos': 'NOUN'}, {'token': "'s", 'lemma': "'s", 'pos': 'PART'}, {'token': 'dick', 'lemma': 'dick', 'pos': 'NOUN'}, {'token': 'one', 'lemma': 'one', 'pos': 'NUM'}, {'token': 'wor', 'lemma': 'wor', 'pos': 'NOUN'}, {'token': 'overrated', 'lemma': 'overrated', 'pos': 'ADJ'}]
  },
}
````
#### Database di buffer
 Database dove mantenere le risorse lessicali e i messaggi di twitter (questi poi verranno recuperati come uno stream teoricamente infinito di dati)
##### Schema di *messaggio_twitter*
###### MongoDB
Per ogni collezione corrispondente ad una emozione abbiamo il seguente schema:  
````
{
    _id: ObjectId(...),
    message: str,
}
````
###### MySQL
![](res/immagini_readme/messaggio_twitter_table_schema.png)

##### Schema di *risorsa_lessicale*
###### MongoDB
Per ogni collezione corrispondente ad una emozione abbiamo il seguente schema:  
````
{
    _id: ObjectId(...),
    lemma:str,
    risorse: {
        EmoSN: Optional[int],
        NRC: Optional[int],
        sentisense: Optional[int],
    }
}
````
###### MySQL
![](res/immagini_readme/risorsa_lessicale_table_schema.png)
#### Pipeline di **preprocessing** dei tweets in python
- [x] Eliminare USERNAME e URL
- [x] processare gli hashtag: possiamo contarli e fare statistiche anche su quelli o possiamo buttarli
- [x] processare emoji ed emoticons: contarli per fare statistiche e trovare sovrapposizioni di uso tra diverse emozioni
- [x] tokenization, lemmatization and pos tagging con *spacy*
- [x] riconoscere le forme di slang e sostituirle con le forme lunghe
- [x] eliminare stop words
- [x] remove punteggiatura, parole mal formate e eventuali caratteri speciali
- [x] trasformare tutto a lower case

#### Database di analytics
 database dove mantenere le statistiche elaborate richieste:
- per ogni emozione (sentimento) dove X è un tipo di risorsa e Y è un sentimento:
  - parole più **frequenti** nei tweet (graficamente visualizzate con una word cloud)
  - emoji più **frequenti** nei tweet (graficamente visualizzate con una word cloud)
  - emoticons più **frequenti** nei tweet (graficamente visualizzate con una word cloud)
  - hashtags più **frequenti** nei tweet
  - la percentuale delle parole delle risorse lessicali presenti nei tweets: _perc_persence_lex_words(X,Y)_ (visualizzarle con un istogramma)
  - raccogliere le parole nuove presenti nei tweets ma non nelle risorse lessicali (_N_twitter_words(Y)- N_shared_words(X,Y)_)
##### Schema di *token_twitter*
###### MongoDB
Per ogni collezione corrispondente ad una emozione abbiamo il seguente schema:  
````
{
    _id: ObjectId(...),
    token: str,
    lemma: str,
    pos: str,
    type: <"word","emoji","emoticon","hashtag">,
}
````
a cui verrà aggiunto il campo `quant` (quantità del lemma trovato)
###### MySQL 
> parola
![](res/immagini_readme/parola_contenuta_table_schema.png)
> emoji

> emoticon

> hashtag

#### eventualmente nuova risorsa su DB
 Memorizzare le _nuove parole_ trovate nei tweet ma assenti nelle risorse fornite (se alla fine del conteggio saranno altamente presenti avremo trovato nuova parole da aggiungere alle risorse o avremo creato una risorsa  aggiuntiva!)
![image](https://user-images.githubusercontent.com/43850400/118098215-ea947000-b3d3-11eb-9a94-4d41571c25f8.png)

### Dove fare Map-Reduce
> Bisogna ipotizzare che i dati siano sharded, quindi divisi su più server

1. Quando si ottengono le statistiche (è un'aggregazione, una reduce)
2. Per aggregare gli stessi lemmi trovati nei messaggi e contarli
## Cosa ho usato del materiale messo a disposizione dalla prof
[X] emoticons
[ ] emoji (ho usato una lib)
[X] risorse lessicali EmoSN, sentisense, NRC
## Osservazioni su Risorse messaggi Twitter
### Tag
USERNAME : indica un username di un utente Twitter.  
URL : indica un url.

Altri tag potrei cercarli con uno script python
## Osservazioni su Risorse lessicali emozioni
Ricordiamo il modello delle emozioni che dobbiamo considerare nel progetto
![image](res/immagini_readme/emotion_model.png)

Adesso vediamo invece come sono organizzate le risorse a disposizione:
- Ogni cartella contiene risorse su una determinata **emozione** ad eccezione di:
    - `_MACOSX` inutile
    - `ConScore` contiene tsv file per associare ad ogni valore uno score
    - `Neg` e `Pos` contengono parole rispettivamente Negative e Positive 
    - `Like-Love` sembrerebbe contenere parole di queste due emozioni, comunque in file separati
    - `Disgust-Hate` come sopra
     
- Ci sono 3 tipi di file:
    - `EmoSN_<emozione>.txt`
    - `NRC_<emozione>.txt`
    - `sentisense_<emozione>.txt`
- Le emozioni presenti sono:
    - **Anger**
    - **Anticipation**
    - **Disgust**
    - Hate
    - **Fear**
    - Hope
    - **Joy**
    - Like
    - Love
    - **Sadness**
    - **Surprise**
    - **Trust**  
    
Quelle in grassetto sono le emozioni presenti anche nei file di `Twitter messaggi` col seguente formato `dataset_dt_<emozione.lower()>_60k.txt`
### Descrizione risorse
![image](res/immagini_readme/lexica_organization.png)
- **EmoSN**: EmoSenticNet includes 13,189 entries for the six Ekman’s emotions of Joy, Sadness, Anger, Fear, Surprise and Disgust. The resource was developed by assigning WordNet Affect emotion labels to SenticNet concepts [Poria et al. 2013; Poria et al. 2014]. The last one is a list of common-sense knowledge concepts with a polarity score [Cambria et al. 2014] referring to the multidisciplinary approach of Sentic Computing [Cambria and Hussain 2015].
- **SS**: SentiSense is a concept-based affective lexicon with a wide set of categories developed by Carrillo de Albornoz [Carrillo de Albornoz et al. 2012], including 5,496 words and 2,190 synsets from WordNet, labeled with an emotion from a set of 14 categories.
- ANEW: The dictionary Affective Norms for English Words includes terms rated from 1 to 9 for each of the three dimensions of Valence, Arousal and Dominance.
- DAL: The Dictionary of Affective Language developed by Whissell [Whissell 2009] contains words belonging to the dimensions of Pleasantness, Activation and Imagery. The 8,742 terms are rated in a three-point scale.
## Osservazioni modello dei dati
### Modello dei dati
[Modello dei dati](res/conceptual-schema-data-project.pdf)
### Osservazioni
- Per operare le generalizzazioni è più facile con MongoDB poichè i documenti si adattano più facilmente alle specializzazioni. In un futuro potrebbero aumentare le specializzazioni e quindi il modello di database a documento risulta più flessibile
## Informazioni amministrazione database

### MongoDB

#### username
> Admin

#### password
> Admin

#### url
##### Atlas
> mongodb+srv://admin:admin@cluster0.9ajjj.mongodb.net/
##### Locale

### MySQL
#### username
> root
#### password
nessuna
#### url
> jdbc:mysql://localhost:3306?serverTimezone=UTC