import email
from email.parser import BytesParser
from email import policy
from email.utils import parseaddr
from requests_html import HTML


def parse(mail_string):
    mail = BytesParser(policy=policy.default).parsebytes(mail_string)
    data = {}
    data['subject'] = mail['subject']
    print("debug")
    print(mail['to'])
    print("debug")
    data['eto'] = [parseaddr(to)[1] for to in mail['to'].split(',')]
    data['efrom'] = parseaddr(mail['from'])[1]
    simplest = mail.get_body(preferencelist=('plain', 'html'))
    plain = ''.join(simplest.get_content().splitlines(keepends=True))
    data['content'] = HTML(html=plain).text

    data['attachment_name'] = []

    for part in mail.iter_attachments():
        fn = part.get_filename()
        data['attachment_name'].append(fn)
    return data


if __name__ == "__main__":
    test = open("2097188.eml", "rb").read()
    print(parse(test))
