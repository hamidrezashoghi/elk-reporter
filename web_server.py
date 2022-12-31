import logging
from datetime import datetime
from flask import Flask, request, render_template, send_file
from elasticsearch_tocsv import elasticsearch_tocsv


class WebServer:
    app = Flask(__name__)

    def __init__(self, web_server_ip, web_server_port, es_host, es_port, es_username, es_password):
        self.web_server_ip = web_server_ip
        self.web_server_port = web_server_port
        self.es_host = es_host
        self.es_port = es_port
        self.es_username = es_username
        self.es_password = es_password
        self.es_instance = self.elastic_conn()

    def elastic_conn(self):
        args = {
            'host': self.es_host, 'port': self.es_port, 'user': self.es_username, 'password': self.es_password,
            'url_prefix': 'http', 'verify': False
        }
        try:
            return elasticsearch_tocsv.build_es_connection(args)
        except:
            return "Couldn't connect to elasticsearch server"

    def run(self):
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.add_url_rule(rule='/', view_func=self.index, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/download', view_func=self.download, methods=['POST'])
        self.app.run(host=self.web_server_ip, port=self.web_server_port)

    def index(self):
        return render_template("index.html")

    def download(self):
        if request.method == 'POST':
            index_name = request.form['index_name']
            query = request.form['query']
            starting_date = request.form['starting_date']
            ending_date = request.form['ending_date']
            csv_seperator = request.form['csv_seperator']
            fields = request.form['fields']

            if query in (None, ' ', ''):
                query = '*'

            try:
                starting_date_obj = datetime.strptime(starting_date, '%Y-%m-%d %H:%M:%S')
                starting_date_millisec = int(starting_date_obj.astimezone().timestamp() * 1000)
            except:
                logging.error(f"starting date format is false. {starting_date}")
                return "starting date format is false"

            try:
                ending_date_obj = datetime.strptime(ending_date, '%Y-%m-%d %H:%M:%S')
                ending_date_millisec = int(ending_date_obj.timestamp() * 1000)
            except:
                logging.error(f"ending date format is false. {ending_date}")
                return "ending date format is false"

            if csv_seperator not in (',', '|'):
                csv_seperator = ','

            if not fields:
                logging.error(f"fields value has incorrect format. {fields}")
                return f"fields value has incorrect format. {fields}"
            else:
                fields = fields.strip().split(',')
            fields.append('empty')

            print(index_name, query, starting_date_millisec, ending_date_millisec, csv_seperator, fields)
            fp_name = datetime.utcnow().strftime('%Y%m%d%H%M%S')

            args = {'url_prefix': 'http', 'host': self.es_host, 'port': self.es_port, 'user': self.es_username,
                    'password': self.es_password, 'verify': False, 'index': index_name, 'starting_date': '@timestamp',
                    'ending_date': '@timestamp', 'log': logging, 'export_path': fp_name + '.csv', 'fields_to_export': fields,
                    'metadata_fields': ["_score"], 'query_string': query, 'time_field': '@timestamp',
                    'count_url': 'https://' + self.es_host + ':' + self.es_port + '/', 'certificate_path': '',
                    'count': 10000, 'disable_progressbar': True, 'scroll_timeout': '10s', 'batch_size': 7500,
                    'fields': fields, 'csv_separator': ',', 'decimal_separator': '.', 'decimal_rounding': 4,
                    'partial_csv_size': 10000000, 'enable_multiprocessing': True, 'timezone': 'Asia/Tehran'}

            elasticsearch_tocsv.fetch_es_data(es_instance=self.es_instance, args=args,
                                              starting_date=str(starting_date_millisec),
                                              ending_date=str(ending_date_millisec), process_name=fp_name)

            return send_file(path_or_file=fp_name + '_process' + fp_name + '_00001.csv', as_attachment=True)
