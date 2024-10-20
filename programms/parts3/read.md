## presentation

## application
    複数のentityの処理はこの層で調整
    分割してdomain serviceを呼び出す

## domain
    modelを含有
    単一のentityの処理はこの層
    =引数のentityは1つまで

## infrastructure
    application/domain layerからのみ呼び出し
    戻り値はentity or DTO
    引数はprimitiveな変数 or DTO

## DB