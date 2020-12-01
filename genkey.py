#need to add argparser
from OpenSSL import crypto

# create a key pair
k = crypto.PKey()
k.generate_key(crypto.TYPE_RSA, 4096)

# create a self-signed cert
cert = crypto.X509()
cert.get_subject().C = "US"
cert.get_subject().ST = "Detroit"
cert.get_subject().L = "Nscope Security"
cert.get_subject().OU = "DevOps"
cert.get_subject().CN = "FireStorm"
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10*365*24*60*60)
cert.set_issuer(cert.get_subject())
cert.set_pubkey(k)
cert.sign(k, 'sha256')

with open("./certs/cacert.crt", "wb") as cert_f:
    cert_f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
with open("./certs/cert.pem", "wb") as key_f:
    key_f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k)) 


