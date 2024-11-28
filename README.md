# Excel2MaiML
## A：実行方法
### [入出力データ]
- 入力データ　　※条件等は下記[B:詳細]を参照
  1. document,protocolのコンテンツをもつMaiMLデータファイル <br/>
　　INPUT/maiml/input.maiml  or  INPUT/xxxxx/yyyyyy.maiml 
  1. 計測の情報をもつエクセルデータ<br/>
　　INPUT/excel/input.xlsx  or  INPUT/xxxxx/zzzzzz.xlsx
- 出力データ
  1. 入力データをマージしたMaiMLファイル <br/>
　　OUTPUT/output.maiml
 
### [実行方法]
- その１.
  1. 入力ファイルを準備 <br/>
　　/INPUT/maiml/ ディレクトリにMaiMLファイル <br/>
　　/INPUT/excel/ ディレクトリにエクセルファイル <br/>
　　/INPUT/others/ ディレクトリに外部ファイル <br/>
　1. コマンド実行 <br/>
　　python3 excel2maiml.py <br/>
- その２.
  1. 入力ファイルを準備 <br/>
　　/INPUT/XXXXX/　ディレクトリにMaiMLファイル、エクセルファイル、外部ファイル　 <br/>
　　　※'XXXXX'は任意の名前 <br/>
　1. コマンド実行 <br/>
　　python3 excel2maiml.py XXXXX <br/>


## B:詳細
### [入力するMaiMLデータ]
  ・program１つを保証 <br/>

### [入力するエクセルデータ]
　・シート名はmethodのID <br/>
　・１行目 <br/>
　　・１列目　’’ <br/>
　　・２列目以降にinstructionのID、もしくは、templateのID <br/>
　・２行目 <br/>
　　・１行目がtemplateのIDの列 <br/>
　　・２行目にprotocol以下がもつpropertyのキー名 <br/>
　・３行目以降は計測データ（複数行＝複数回計測） <br/>
　　・１列目にresultsのID <br/>
　　　・１行目がinstructionのIDの列 <br/>
　　　・３行目以降に計測した日時 <br/>
　　・１行目がtemplateのIDの列 <br/>
　　　・３行目以降にpropertyのキーに対する値 <br/>

### ［作成するMaiMLデータ］
  ・複数回の計測データをもつ場合はresultsを複数作成 <br/>
  　　（１行のデータ→results１つ） <br/>
  ・汎用データコンテナはpropertyのみ作成 <br/>
  ・入力MaiMLファイルのtemplateをインスタンスとしてコピーする <br/>
  ・templateがもつ汎用データコンテナのkeyとエクセルのkeyが一致した場合のみvalueをエクセルデータで更新 <br/>
  　　（一致しなければ、エクセルデータは無視される） <br/>
  ・エクセルの２行目に'INSERTION'が存在した場合はtemplateIDに基づくインスタンスにinertionコンテンツを作成 <br/>
  　1. INPUTディレクトリに外部ファイルが存在する場合 <br/>
  　　insertionのコンテンツ　uri : ./+ファイル名、hash値：ファイルから算出したhash値 <br/>
  　1. INPUTディレクトリに外部ファイルが存在しない場合 <br/>
　  　insertionのコンテンツ　uri : ./+ファイル名、hash値：空 <br/>
  ・eventLogを１つ作成 <br/>
  ・計測日時のデータが存在する場合にtraceを作成 <br/>
　・複数回の計測データをもつ場合はtraceを複数作成 <br/>
　・エクセルデータにinstructionIDが存在し、かつ、日時のデータが存在する場合にeventを１つ作成 <br/>
　　　key=lifecycle:transitionのvalueがcompleteのみ <br/>


## C:python実行環境の構築
### [pythonバージョン]
  ・3.12.x <br/>
### [pythonパッケージ]
  ・requirements.txt <br/>
