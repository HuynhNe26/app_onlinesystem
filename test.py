import hmac
import hashlib

secret_key = "K951B6PE1waDMi640xX08PD3vg6EkVlz"

data = {
    "accessKey": "F8BBA842ECF85",
    "amount": "229000",
    "extraData": "{\"id_package\":3,\"id_user\":8}",
    "message": "Successful.",
    "orderId": "11c344cb96fd",
    "orderInfo": "Gói PRO",
    "orderType": "momo_wallet",
    "partnerCode": "MOMO",
    "payType": "qr",
    "requestId": "MOMO_1234567890",
    "responseTime": 1731900000000,
    "resultCode": 0,
    "transId": 1234567890
}

raw = (
    f"accessKey={data['accessKey']}"
    f"&amount={data['amount']}"
    f"&extraData={data['extraData']}"
    f"&message={data['message']}"
    f"&orderId={data['orderId']}"
    f"&orderInfo={data['orderInfo']}"
    f"&orderType={data['orderType']}"
    f"&partnerCode={data['partnerCode']}"
    f"&payType={data['payType']}"
    f"&requestId={data['requestId']}"
    f"&responseTime={data['responseTime']}"
    f"&resultCode={data['resultCode']}"
    f"&transId={data['transId']}"
)

sign = hmac.new(
    secret_key.encode(),
    raw.encode(),
    hashlib.sha256
).hexdigest()

print(sign)
