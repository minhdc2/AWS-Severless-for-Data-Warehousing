
import support.func_web_scraping as sfws
import datetime
import pandas as pd
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

def crawl_vnindex_demo(url_path,
                       from_to_date_input,
                       onclick,
                       destination='./data/'):
    soup = sfws.parse_html_using_search_bar_with_selenium(url_path,
                                                          input=from_to_date_input,
                                                          onclick=onclick)
    table_tag = soup.find('table',
                          {'id': 'owner-contents-table'})
    if table_tag:
        print(url_path + ' Found a table!')
        src_df = pd.read_html(str(table_tag).upper())[0]
        removed_columns = [('GIÁ (NGHÌN VNĐ)', 'ĐIỀU CHỈNH'),
                           ('Unnamed: 11_level_0', 'Unnamed: 11_level_1'),
                           ('Unnamed: 12_level_0', 'Unnamed: 12_level_1')]
        org_columns = list(src_df.columns)
        print(org_columns)
        for column in org_columns:
            if column in removed_columns:
                del src_df[column]

        columns = ['RECORDED_DATE', 'CLOSE_PRICE', 'INDEX_CHANGE', 'MACHED_VOLUME', 'MACHED_AMOUNT',
                   'SELF_DEALED_VOLUME', 'SELF_DEALED_AMOUNT', 'OPEN_PRICE', 'HIGHEST_PRICE', 'LOWEST_PRICE']
        src_df = pd.DataFrame(src_df.values, columns=columns)
        print(src_df.head())

    filename = list(from_to_date_input.values())[0][:10]
    filename = filename.replace("/", "")
    filepath = destination + filename + '.csv'
    src_df.to_csv(filepath, index=False)
    src_df = src_df.to_json()
    return src_df

@app.route('/')
def index():
    return "<h1>Hello</h1>"

class command(Resource):

    def get(self):
        print("The program is running!")
        url_path = "" #removed url
        today = datetime.datetime.now().strftime('%d/%m/%Y')
        from_to_date_input = {
            "//input[@name='daterange']": f"{today} - {today}",
        }
        onclick = "//div[@onclick='ownerCDL.handleFindDisclosure()']"
        src_df = crawl_vnindex_demo(url_path=url_path,
                           from_to_date_input=from_to_date_input,
                           onclick=onclick)

        return src_df, 200

api.add_resource(command, '/data')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

