from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, validators, RadioField, SubmitField
from subprocess import check_call

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class QueryForm(Form):
    start_date = TextField('Start date:', validators=[validators.required(),
                validators.Regexp('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$', flags=0, message=None)])
    end_date = TextField('End date:', validators=[validators.required(),
                validators.Regexp('(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$', flags=0, message=None)])
    src_ip4 = TextField('Source IP:', validators=[validators.optional(), validators.Length(min=5, max=45)])
    dst_ip4 = TextField('Destination IP:', validators=[validators.optional(), validators.Length(min=5, max=45)])
    protocol = RadioField('Protocol:', choices=[('all', 'All'), ('tcp', 'TCP'), ('udp', 'UDP')],
               default='All', validators=[validators.required()])

    def validate(self):
        if not super(QueryForm, self).validate():
            return False

        if not self.src_ip4.data and not self.dst_ip4.data:
            msg = 'At least one of Source and Destination IP must be set'
            self.src_ip4.errors.append(msg)
            self.dst_ip4.errors.append(msg)
            return False

        return True

@app.route("/", methods=['GET', 'POST'])

def query_form():
    form = QueryForm(request.form)

    print form.errors
    if request.method == 'POST':

        if form.validate():
            flash('Query running. Please wait... ')

            qry_params = {}

            qry_params['start_dt'] = request.form['start_date'] + ":00"
            # Verify date format

            # Verify date format
            qry_params['end_dt'] = request.form['end_date'] + ":00"

            # Verify regex
            qry_params['src_regex'] = request.form['src_ip4']

            # Verify regex
            qry_params['dst_regex'] = request.form['dst_ip4']

            # Verify protocol
            qry_params['protocol'] = request.form['protocol']

            run_query(**qry_params)

        else:
            flash('Error: Query parameters incomplete. ', request.form.errors)


    return render_template('flow-query.html', form=form)

def run_query(**qry_params):

    # Construct protocol filter flag
    flags = { 'tcp' : '-r6', 'udp' : '-r17', 'all' : '' }
    proto_flag = flags[ qry_params['protocol'] ]

    # Construct command
    cmd = "flow-cat -t \'" + qry_params['start_dt'] + "\' -T \'" + qry_params['end_dt'] + "\' /var/flows/max/*/*/*/ft-v05.*" + \
          " | flow-filter " + proto_flag + \
          " | flow-print -n -f3" + \
          " | pcregrep -C1 \'" + qry_params['src_regex'] + "\'" + \
          " > /tmp/output.txt"

    print cmd
    check_call(cmd, shell=True)

if __name__ == "__main__":
    app.run()

