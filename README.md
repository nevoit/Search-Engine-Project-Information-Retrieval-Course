Our search engine was implemented with a Model-View-Controller (MVC) Architecture.

Example of our GUI:
![GUI](https://github.com/nevoit/Information-Retrieval/blob/master/Resources/a.png "GUI")

The Structure:
=============

1.	Select the next 'parts percentage (%), of the documents from the corpus ('parts' being a pre-defined variable in Config.ini)
2.	Send these documents to the Parser.
3.	Optional: send the output of the Parser to the Stemmer.
4.	Send the output to the Indexer. The Indexer will create a temporary index file for the documents from step one.
5.	Go back to step one until the coverage will be 100 percentage.
6.	Create final posting file from all the temporary files that were created in step 4.
7.	Finish the preprocessing stage.

The Model:
=============

 - ReadFile – This module reads documents from the corpus.

- Parser – Parses the documents (removes stop-words, converts dates to a unified format etc.).

- Stemmer – Performs stemming on a given document. We used nltk for Python.

- Indexer – Creates the final posting file separated by alphabet letters.

- Searcher – Runs the query and returns the relevant results.

- Ranker – This model will rank each document given a specific query from the user (from the GUI).  We used Cosine similarity (With TF, IDF), BM 25, 

- WriteFile – This module writes files to the disk.

- GUI (view) – A window divided into 3 parts. The left part consists of the query input and several checkboxes the user can use. The middle part shows the documents that the engine found most relevant. The user can either enter a query or choose a file with multiple queries. The right side shows the contents of a given document ID (such as the one you can see in the result window)

![GUI](https://github.com/nevoit/Information-Retrieval/blob/master/Resources/b.png "GUI")
![GUI](https://github.com/nevoit/Information-Retrieval/blob/master/Resources/c.png "GUI")

Licence:
=============

Copyright 2018 Nevo Itzhak and Tomer Shahar

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
