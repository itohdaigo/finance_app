import pandas as pd
import yfinance as yf
import altair as alt #alyair を組み込むために必要
import streamlit as st


st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
"""
)

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider('日数',1,50,20)#スライダーを作成し、日付に格納

#これにより、スライダーで選択した日にちが見出しに表示される
st.write(f"""
### 過去**{days}日間**のGAFAのデータ

""")


@st.cache#これで、キャッシュに置く事ができる
def get_data(days,tickers):#データを取得する処理を関数にまとめる
    df = pd.DataFrame()#データ構造を取得

    for company in tickers.keys():
        # print(company)#これにより、tickersの要素数分、上から会社名を出力する
        tkr = yf.Ticker(tickers[company])  # AAPLは、ティッカーシンボル。
        # tickers[company]で、tickerリスト内の、会社名の部分を抜き出す
        hist = tkr.history(period=f'{days}d')  # 20日分の株価データを取得
        hist.index = hist.index.strftime('%d %B %Y')  # YはYear 日付のフォーマットの変更

        hist = hist[['Close']]  # Closeのみ使用する
        hist.columns = [company]  # 列名を会社名にする
        hist = hist.T  # 行と列を交換する
        hist.index.name = 'Name'

        df = pd.concat([df, hist])  # pdのdfというデータに対して、件数histを追加していく。
        #print(df)#確認用
    return df

try:#例外処理が起こった場合の処理を記載するため。
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        '範囲を指定して下さい',
        0.0, 3500.0, (0.0, 3500.0)  # これにより、左右から動かす事ができる。
    )

    tickers = {  # 会社名とティッカーシンボルを紐付けて格納
        'apple': 'AAPL',
        'facebook': 'FB',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN',
    }

    df = get_data(days, tickers)  # 日にちと会社を取得

    companies = st.multiselect(  # 会社名を選択
        '会社名を選択して下さい。',
        list(df.index),  # 会社名をリスト化する
        ['google', 'apple', 'facebook', 'amazon']  # デフォルトの表示を設定
    )

    if not companies:  # もし会社名が何もない（一つも選択されてないなら）
        st.error('少なくとも一社は選択して下さい')

    else:  # 選択されているなら
        data = df.loc[companies]  # 選択した企業のデータを取得
        st.write("### 株価（USD）", data.sort_index())  # 選択した会社を整列して表示

        data = data.T.reset_index()  # これで、列と行の属性を逆転
        data = pd.melt(data, id_vars=['Date']).rename(columns={'value': 'Stock Prices(USD)'})  # これにより、日付、企業名、株価
        # また、renameにて、株価の列の値段をvalueから、Stock Prices(USD)に変更している

        chart = (  # チャートの部分
            alt.Chart(data).mark_line(opacity=0.8, clip=True).encode(x="Date:T",
                                                                     y=alt.Y("Stock Prices(USD):Q", stack=None,
                                                                             scale=alt.Scale(domain=[ymin, ymax])),
                                                                     color='Name:N')
            # mark_lineで、折れ線グラフを表示。encodeで、横縦軸の設定をしている
        )
        st.altair_chart(chart, use_container_width=True)  # 上のチャートを表示する Trueで、コンテナのサイズに合わせる
except:
    st.error("###エラーがおきました！？")