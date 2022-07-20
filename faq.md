#### Q: How does the translation of natural language into a SQL query work? 
A: The translation uses OpenAI Codex APIs. The underlying model needs the following inputs: 
- Table structure (table name, column names) 
- A simple question in english language
The model returns a SQL query.

#### Q: Is this a fancy AI experiment or does it really work? 
A: Codex model is a very deep intelligence that was developed using code from the whole of Github. This intelligence also powers "Github Co-Pilot", a tool to make code suggestions for programmers. Other apps using Codex are listed [here](https://openai.com/blog/codex-apps/).
We have tried the model with simple structure of 5 tables. The results are very good !

#### Q:Will it work with the complex data landscape at WBL bank?
A: The  intelligence is very good at constructing queries as long as the table and column names are explanatory. Its performance with a complex set of tables (like WBL Bank) needs to be tested. 
It is probably safe to say that the model will needs data sets prepared for data analysis - rather than raw application tables.

#### Q: How will the AI understand banking terminology or lexican specific to our data? 
A: The model is not trained for a specific domain, such as banking. Hence it is likely that it may not understand banking terminology. A likley solution is to use explanatory column names (e.g. utilization rate) so that the model can associate the column with a question on utilization; without having to know its meaning.  

#### Q: Do we ned to give our data to the model? 
A: No. The model just needs table and column names. 

#### Q: Can the AI model be trained on our data? 
A: Yes. For training the model, we need to provide a set of natural lanuguage questions and the right SQL query. 

#### Q: What happens if the AI makes a mistake? 
A: It is possible (even likely) that the AI will make some mistakes. We need to work out a process that the mistakes are used for model improvement and there is are checks / balances in place to ensure key decisions are made with the right data. As our confidence in the solution increases, we will reduce / remove the checks. 

#### Q: Is it better to expose our C360 to the Product Managers via an excel or Qlikview instead? 
A: A typical C360 has hundreds of columns. This makes it a very bulky excel. It is not possible for Product Mangers to comprehend / use this excel. On the otehr hand, technology teams find it difficult to design a neat interface to access it. Hence the C360 is only used by Data Analysts - and not by the Product Managers. 

#### Q: We have documented the right metadata in Collibra. Can the product managers use Collibra instead?
A: Product Managers need real data to make decisions; not metadata. 

