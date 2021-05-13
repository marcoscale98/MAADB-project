# MAADB-project
Progetto d'esame per MAADB
## Schema di lavoro
[Descrizione progetto](https://docs.google.com/document/d/1i3TSJpyr4vw-edKBX1XNuy52f8_Sem0aPWmo6fBpuBs/edit?ts=57308c63#heading=h.oublcismo327)
### Cosa c'è da creare?
- **Database di backup**: database dove mantenere le risorse lessicali e i messaggi di twitter (questi poi verranno recuperati come uno stram teoricamente infinito di dati)
- Pipeline di **preprocessing** dei dati testuali in python (con lib. *nltk* oppure *gensim*)
- **Database di analytics**: database dove mantenere le statistiche elaborate richieste:
  - parole più **frequenti** nei tweet (graficamente visualizzate con una word cloud)
  - emoji più frequenti nei tweet (graficamente visualizzate con una word cloud)
  - emoticons più frequenti nei tweet (graficamente visualizzate con una word cloud)
  - per ciascun sentimento, la percentuale delle parole delle risorse lessicali presenti nei tweets (visualizzarle con un istogramma)
  - raccogliere le parole nuove presenti nei tweets ma non nelle risorse lessicali (N_twittter_words(Y)- N_shared_words(X,Y))
![image](https://user-images.githubusercontent.com/43850400/118098215-ea947000-b3d3-11eb-9a94-4d41571c25f8.png)
