program fileを修正するならpart内部から！
内部には役割ごとの部分関数があります。
修正・デバッグしてから問題なければ全体のコードに反映してください。

全体のコードは3つのパッケージに分割されます
1.Clientパッケージ
　KeepaClient, DatabaseClient, AmazonAPIClient, ImageSearcherクラスが含まれます
2.Repositoryパッケージ
    Manegerクラスのためのrepositoryが含まれます
3.Managerパッケージ
    FacadeパターンをとるManagerクラスが含まれます