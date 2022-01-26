"""Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'client_secrets.json'
VIEW_ID = '254844841'


def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:sessions'}],
          'dimensions': [{'name': 'ga:country'}]
        }]
      }
  ).execute()


def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
  print(response)
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        print(header + ': ', dimension)

      for i, values in enumerate(dateRangeValues):
        print('Date range:', str(i))
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          print(metricHeader.get('name') + ':', value)


def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)

  print_response(response)

if __name__ == '__main__':
  main()



def signup():

    method = request.args['method']
    
    username = request.form.get('username')
    
    email = request.form.get('email')
    password = request.form.get('password')

    existing_email = User.objects(email=email)
    
    if method == 'google':
        iid = gen_id(7)
        username = iid
        password = gen_pass()

        if existing_email:
            #login user
            user = User.objects(email=email)
            if user:
                user = user[0]._data
                del user['password']
                user['id'] = str(user['id'])
                token = gen_token(email)

                songs = get_songs(user)
                return {'user': user, 'token': token}
    
    iid = gen_id(7)
    hashed_pass = bcrypt.generate_password_hash(password)
    existing_username = User.objects(username=username)
    if existing_username:
        return {'message' : f'User with username {username} already exists!'}, 400
    if existing_email:
        return {'message' : f'User with email {email} already exists!'}, 400
    user = User()
    for key, value in request.form.items():
        setattr(user, key, value)
    if not validate_email(email):
        return {'message' : f'Please enter a valid email address.'}, 400
    user.password = hashed_pass.decode()
    user.iid = iid
    user.username = username
    try:   
               
        token = gen_token({'email' : email, 'username' : username, 'iid' : iid, 'password' : user.password}, 48)
  
        url = f'{os.getenv("CLIENT_URL")}/auth/confirm?token={token}'
        
        return send_email(
            subject= "TunedBass validation email",
             message = f"""
             <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type="text/css">
    
    
                .TunedBass{{
                    font: medium/ 1.5  Arial,Helvetica,sans-serif !important;
                    margin: auto;
                    padding: 10px;
                    color: black;
                   
                }}
    
    
                   
                  
    
                .btn {{
                    cursor: pointer;
                    display: inline-block;
                    min-height: 1em;
                    outline: 0;
                    border: none;
                    vertical-align: baseline;
                    background: #e0e1e2 none;
                    color: rgba(0,0,0,.6);
                    font-family: Lato,"Helvetica Neue",Arial,Helvetica,sans-serif;
                    margin: 0 .25em 0 0;
                    padding: .78571429em 1.5em;
                    text-transform: none;
                    text-shadow: none;
                    font-weight: 600;
                    line-height: 1em;
                    font-style: normal;
                    text-align: center;
                    text-decoration: none;
                    border-radius: .28571429rem;
                    box-shadow: inset 0 0 0 1px transparent,inset 0 0 0 0 rgba(34,36,38,.15);
                    -webkit-user-select: none;
                    -ms-user-select: none;
                    user-select: none;
                    transition: opacity .1s ease,background-color .1s ease,color .1s ease,box-shadow .1s ease,background .1s ease;
                    will-change: "";
                    -webkit-tap-highlight-color: transparent;
                }}
                .btn-primary {{
                    color: #fff !important;
                    background-color: #0d6efd !important;
                    border-color: #0d6efd !important;
                    
                }}
        </style>
    </head>
    <body>
    
        <div class="TunedBass">
    
        <h1>Thank you for signing up to TunedBass!</h1>
    
        <p>To finish up, Click the button to verify your account.</p>
        <a href="{url}" target="_blank" class="btn btn-primary">Verify</a>
        
        <p>If button did not work use this link:</p>
        <a href="{url}" target="_blank">{url}</a>
    
        <h3>The verification is valid for only 48hrs</h3>
    
        <p>For support please contact us at <a href="mailto:admin@tunedbass.com">admin@tunedbass.com</a></p>
        </div>
        
    </body>
    </html>
             """ ,
              recipients=[email],
               res='DONE')
        
    except Exception as e:
        print(e)
        return Response(
            response= 'Something went wrong!',
            status= 500,
        )
