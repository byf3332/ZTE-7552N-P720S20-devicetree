#!/usr/bin/env python3
import sys
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} DECRYPT_CPP")

path = Path(sys.argv[1])
text = path.read_text()
marker = "P720S20: reject an empty Gatekeeper hardware auth token"

if marker in text:
    print(f"P720S20 Gatekeeper token guard already installed in {path}")
    raise SystemExit(0)

old = '''\t\t\tandroid::hardware::hidl_vec<uint8_t> gk_pwd_token_hidl;
\t\t\tGKResponse gkResponse;
\t\t\tgk_pwd_token_hidl.setToExternal(const_cast<uint8_t *>((const uint8_t *)gk_pwd_token), SHA512_DIGEST_LENGTH);
\t\t\tandroid::hardware::Return<void> hwRet =
\t\t\t\tgk_device->verify(fakeUid(user_id), 0 /* challenge */,
\t\t\t\t\t\t\t\t  pwd_handle_hidl,
\t\t\t\t\t\t\t\t  gk_pwd_token_hidl,
\t\t\t\t\t\t\t\t  [&gkResponse]
'''

new = f'''\t\t\tandroid::hardware::hidl_vec<uint8_t> gk_pwd_token_hidl;
\t\t\tGKResponse gkResponse;
\t\t\tbool gatekeeper_token_added = false;
\t\t\tgk_pwd_token_hidl.setToExternal(const_cast<uint8_t *>((const uint8_t *)gk_pwd_token), SHA512_DIGEST_LENGTH);
\t\t\tandroid::hardware::Return<void> hwRet =
\t\t\t\tgk_device->verify(fakeUid(user_id), 0 /* challenge */,
\t\t\t\t\t\t\t\t  pwd_handle_hidl,
\t\t\t\t\t\t\t\t  gk_pwd_token_hidl,
\t\t\t\t\t\t\t\t  [&gkResponse, &gatekeeper_token_added]
'''

if text.count(old) != 1:
    raise SystemExit("unexpected TeamWin Gatekeeper verify source state")
text = text.replace(old, new, 1)

old = '''\t\t\t\t\t\t\t\t\t\tif (rsp.code >= android::hardware::gatekeeper::V1_0::GatekeeperStatusCode::STATUS_OK) {
\t\t\t\t\t\t\t\t\t\t\tgkResponse = GKResponse::ok({rsp.data.begin(), rsp.data.end()});
\t\t\t\t\t\t\t\t\t\t\tconst hw_auth_token_t* hwAuthToken =
\t\t\t\t\t\t\t\t\t\t\t\treinterpret_cast<const hw_auth_token_t*>(gkResponse.payload().data());
'''

new = f'''\t\t\t\t\t\t\t\t\t\tif (rsp.code >= android::hardware::gatekeeper::V1_0::GatekeeperStatusCode::STATUS_OK) {{
\t\t\t\t\t\t\t\t\t\t\tgkResponse = GKResponse::ok({{rsp.data.begin(), rsp.data.end()}});
\t\t\t\t\t\t\t\t\t\t\t// {marker}.
\t\t\t\t\t\t\t\t\t\t\tif (gkResponse.payload().size() < sizeof(hw_auth_token_t)) {{
\t\t\t\t\t\t\t\t\t\t\t\tprintf("gatekeeper returned an invalid hardware auth token\\n");
\t\t\t\t\t\t\t\t\t\t\t\treturn;
\t\t\t\t\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\t\t\t\t\tconst hw_auth_token_t* hwAuthToken =
\t\t\t\t\t\t\t\t\t\t\t\treinterpret_cast<const hw_auth_token_t*>(gkResponse.payload().data());
'''

if text.count(old) != 1:
    raise SystemExit("unexpected TeamWin Gatekeeper payload source state")
text = text.replace(old, new, 1)

old = '''\t\t\t\t\t\t\t\t\t\t\tif (service == NULL) {
\t\t\t\t\t\t\t\t\t\t\t\tprintf("error: could not connect to keystore service\\n");
\t\t\t\t\t\t\t\t\t\t\t\tALOGE("error: could not connect to keystore service\\n");
\t\t\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t\t\t\tauto binder_result = service->addAuthToken(authToken);
'''

new = '''\t\t\t\t\t\t\t\t\t\t\tif (service == NULL) {
\t\t\t\t\t\t\t\t\t\t\t\tprintf("error: could not connect to keystore authorization service\\n");
\t\t\t\t\t\t\t\t\t\t\t\tALOGE("error: could not connect to keystore authorization service\\n");
\t\t\t\t\t\t\t\t\t\t\t\treturn;
\t\t\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t\t\t\tauto binder_result = service->addAuthToken(authToken);
\t\t\t\t\t\t\t\t\t\t\tif (!binder_result.isOk()) {
\t\t\t\t\t\t\t\t\t\t\t\tprintf("failed to add Gatekeeper hardware auth token: %s\\n",
\t\t\t\t\t\t\t\t\t\t\t\t\tbinder_result.getDescription().c_str());
\t\t\t\t\t\t\t\t\t\t\t\treturn;
\t\t\t\t\t\t\t\t\t\t\t}
\t\t\t\t\t\t\t\t\t\t\tgatekeeper_token_added = true;
'''

if text.count(old) != 1:
    raise SystemExit("unexpected TeamWin Keystore authorization source state")
text = text.replace(old, new, 1)

old = '''\t\t\tif (!hwRet.isOk()) {
\t\t\t\tprintf("gatekeeper verification failed\\n");
\t\t\t\treturn Free_Return(retval, weaver_key, &pwd);
\t\t\t}
'''

new = '''\t\t\tif (!hwRet.isOk() || !gatekeeper_token_added) {
\t\t\t\tprintf("gatekeeper verification did not provide a usable hardware auth token\\n");
\t\t\t\treturn Free_Return(retval, weaver_key, &pwd);
\t\t\t}
'''

if text.count(old) != 1:
    raise SystemExit("unexpected TeamWin Gatekeeper result source state")
text = text.replace(old, new, 1)

path.write_text(text)
print(f"Installed P720S20 Gatekeeper hardware auth token guard in {path}")
