import os
import re

def patch_about_page(sp_path):
    if not os.path.exists(sp_path):
        return
    with open(sp_path, "r", encoding="utf-8") as f:
        t = f.read()
    t = re.sub(r"launchUrlString\([\'\"][^\'\"]*(?:privacy\.html|remote-support)[\'\"]\);", "launchUrlString(\'https://yulelink.com/service/remote-support\');", t)
    t = re.sub(r"child:\s*Text\(\s*(?:translate\(\'Privacy Statement\'\)|'[^']*?นโยบาย[^']*?'),", "child: Text(\n                    \'นโยบายการให้บริการ\',", t)
    t = re.sub(r"launchUrlString\([\'\"]https://(?:rustdesk\.com|yulelink\.com)[\'\"]\);", "launchUrlString(\'https://yulelink.com\');", t)
    t = re.sub(r"child:\s*Text\(\s*(?:translate\(\'Website\'\)|'\${translate\(\'Website\'\)}:[^']*'|'[^']*?yulelink\.com[^']*?'),", "child: Text(\n                    \'ยูลลิงก์ ลิงก์ไปด้วยกัน : yulelink.com\',", t)
    t = re.sub(r"(\'Copyright © \${DateTime\.now\(\)\.toString\(\)\.substring\(0, 4\)} Purslane Tech Pte\. Ltd\.)(?: \| Modified by [^\'\n]*)?(\\n\$license\')", r"\g<1> | Modified by Yulelink\g<2>", t)

    with open(sp_path, "w", encoding="utf-8") as f:
        f.write(t)
    print("[CI] desktop_setting_page.dart: Patched About website & policy branding")

def patch_dialog_file(dialog_path):
    if not os.path.exists(dialog_path):
        return
    with open(dialog_path, "r", encoding="utf-8") as f:
        t = f.read()

    crlf = "\r\n" in t
    nl = "\r\n" if crlf else "\n"

    if "final isLocked = bind.mainGetBuildinOption(key: 'lock-server-settings') == 'Y'" in t:
        return

    old_dm = (
        f"  final errMsgs = [{nl}"
        f"    idServerMsg,{nl}"
        f"    relayServerMsg,{nl}"
        f"    apiServerMsg,{nl}"
        f"  ];{nl}{nl}"
        f"  dialogManager.show((setState, close, context) {{"
    )
    new_dm = (
        f"  final errMsgs = [{nl}"
        f"    idServerMsg,{nl}"
        f"    relayServerMsg,{nl}"
        f"    apiServerMsg,{nl}"
        f"  ];{nl}{nl}"
        f"  dialogManager.show((setState, close, context) {{{nl}"
        f"    final isLocked = bind.mainGetBuildinOption(key: 'lock-server-settings') == 'Y' ||{nl}"
        f"        bind.mainGetBuildinOption(key: 'hide-server-settings') == 'Y' ||{nl}"
        f"        isOptionFixed('custom-rendezvous-server');"
    )
    if old_dm in t:
        t = t.replace(old_dm, new_dm, 1)

    old_sub = f"    Future<bool> submit() async {{{nl}"
    new_sub = f"    Future<bool> submit() async {{{nl}      if (isLocked) return false;{nl}"
    if old_sub in t:
        t = t.replace(old_sub, new_sub, 1)

    old_bf_desktop = f"                autofocus: autofocus,{nl}              ).workaroundFreezeLinuxMint(),"
    new_bf_desktop = f"                autofocus: autofocus && !isLocked,{nl}                readOnly: isLocked,{nl}              ).workaroundFreezeLinuxMint(),"
    if old_bf_desktop in t:
        t = t.replace(old_bf_desktop, new_bf_desktop, 1)

    old_bf_mob = f"        validator: validator,{nl}      ).workaroundFreezeLinuxMint();"
    new_bf_mob = f"        validator: validator,{nl}        readOnly: isLocked,{nl}      ).workaroundFreezeLinuxMint();"
    if old_bf_mob in t:
        t = t.replace(old_bf_mob, new_bf_mob, 1)

    old_title = f"          ...ServerConfigImportExportWidgets(controllers, errMsgs),{nl}"
    new_title = f"          if (!isLocked) ...ServerConfigImportExportWidgets(controllers, errMsgs),{nl}"
    if old_title in t:
        t = t.replace(old_title, new_title, 1)

    old_api_warn = f"                  Padding({nl}                    padding: EdgeInsetsDirectional.only("
    new_api_warn = f"                  if (!isLocked){nl}                    Padding({nl}                      padding: EdgeInsetsDirectional.only("
    if old_api_warn in t:
        t = t.replace(old_api_warn, new_api_warn, 1)

    old_actions = (
        f"      actions: [{nl}"
        f"        dialogButton('Cancel', onPressed: () {{{nl}"
        f"          close();{nl}"
        f"        }}, isOutline: true),{nl}"
        f"        dialogButton({nl}"
        f"          'OK',{nl}"
    )
    new_actions = (
        f"      actions: [{nl}"
        f"        if (isLocked){nl}"
        f"          dialogButton('Close', onPressed: () {{{nl}"
        f"            close();{nl}"
        f"          }}, isOutline: false){nl}"
        f"        else ...[{nl}"
        f"          dialogButton('Cancel', onPressed: () {{{nl}"
        f"            close();{nl}"
        f"          }}, isOutline: true),{nl}"
        f"          dialogButton({nl}"
        f"            'OK',{nl}"
    )
    old_actions_end = f"          }},{nl}        ),{nl}      ],{nl}"
    new_actions_end = f"          }},{nl}        ),{nl}        ],{nl}      ],{nl}"
    if old_actions in t and old_actions_end in t:
        t = t.replace(old_actions, new_actions, 1)
        t = t.replace(old_actions_end, new_actions_end, 1)

    old_tf_sig = f"  EdgeInsetsGeometry? contentPadding,{nl}}}) {{"
    new_tf_sig = f"  EdgeInsetsGeometry? contentPadding,{nl}  bool readOnly = false,{nl}}}) {{"
    if old_tf_sig in t:
        t = t.replace(old_tf_sig, new_tf_sig, 1)

    old_tf_body = f"  return TextFormField({nl}    controller: controller,{nl}    decoration: InputDecoration({nl}"
    new_tf_body = (
        f"  return TextFormField({nl}"
        f"    controller: controller,{nl}"
        f"    readOnly: readOnly,{nl}"
        f"    decoration: InputDecoration({nl}"
    )
    if old_tf_body in t:
        t = t.replace(old_tf_body, new_tf_body, 1)

    old_tf_icon = f"      contentPadding: contentPadding,{nl}    ),"
    new_tf_icon = f"      contentPadding: contentPadding,{nl}      suffixIcon: readOnly ? const Icon(Icons.lock_outline, size: 16) : null,{nl}    ),"
    if old_tf_icon in t:
        t = t.replace(old_tf_icon, new_tf_icon, 1)

    with open(dialog_path, "w", encoding="utf-8") as f:
        f.write(t)
    print("[CI] dialog.dart: Patched server dialog with read-only & lock controls")

def main():
    cfg_path = os.path.join("libs", "hbb_common", "src", "config.rs")
    if not os.path.exists(cfg_path):
        print(f"[CI] Warning: {cfg_path} not found")
        return

    with open(cfg_path, "r", encoding="utf-8") as f:
        text = f.read()

    # App name
    text = re.sub(
        r'pub static ref APP_NAME: RwLock<String> = RwLock::new\(.*?\.to_owned\(\)\);',
        'pub static ref APP_NAME: RwLock<String> = RwLock::new("YuleLink".to_owned());',
        text
    )

    # Server
    text = re.sub(
        r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[".*?"\];',
        'pub const RENDEZVOUS_SERVERS: &[&str] = &["x9ragj8s4ydxv89f7m-rustdesk.yulelink.com"];',
        text
    )

    # Key
    text = re.sub(
        r'pub const RS_PUB_KEY: &str = ".*?";',
        'pub const RS_PUB_KEY: &str = "s2J6JDCuo1yTevpB2unpJwYdhIYnd9Qq79dEogH7cGQ=";',
        text
    )

    # Relay server
    if 'pub const RELAY_SERVER:' in text:
        text = re.sub(
            r'pub const RELAY_SERVER: &str = ".*?";',
            'pub const RELAY_SERVER: &str = "";',
            text
        )
    else:
        text = text.replace(
            'pub const RS_PUB_KEY:',
            'pub const RELAY_SERVER: &str = "";\npub const RS_PUB_KEY:'
        )

    # API server
    if 'pub const API_SERVER:' in text:
        text = re.sub(
            r'pub const API_SERVER: &str = ".*?";',
            'pub const API_SERVER: &str = "https://rustdesk-api.yulelink.com";',
            text
        )
    else:
        text = text.replace(
            'pub const RS_PUB_KEY:',
            'pub const API_SERVER: &str = "https://rustdesk-api.yulelink.com";\npub const RS_PUB_KEY:'
        )

    # OVERWRITE_SETTINGS
    # Apply OVERWRITE_SETTINGS (Hard lock at Rust Core level)
    code_ow = """pub static ref OVERWRITE_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new({
        let mut m = HashMap::new();
        m.insert("custom-rendezvous-server".to_string(), "x9ragj8s4ydxv89f7m-rustdesk.yulelink.com".to_string());
        m.insert("key".to_string(), "s2J6JDCuo1yTevpB2unpJwYdhIYnd9Qq79dEogH7cGQ=".to_string());
        m.insert("relay-server".to_string(), "".to_string());
        m.insert("api-server".to_string(), "https://rustdesk-api.yulelink.com".to_string());
        m
    });"""
    pat_ow = r"pub static ref OVERWRITE_SETTINGS: RwLock<HashMap<String, String>> = (?:Default::default\(\)|RwLock::new\(\{.*?\}\));"
    text = re.sub(pat_ow, lambda _: code_ow, text, count=1, flags=re.DOTALL)


    # BUILTIN_SETTINGS
    # Apply BUILTIN_SETTINGS (hide-server-settings & lock-server-settings)
    bi_code = """pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new({
        let mut m = HashMap::new();
        m.insert("lock-server-settings".to_string(), "Y".to_string());
        m
    });"""
    pat_bi = r"pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String, String>> = (?:Default::default\(\)|RwLock::new\(\{.*?\}\));"
    text = re.sub(pat_bi, lambda _: bi_code, text, count=1, flags=re.DOTALL)


    # Ensure get_options and get_option have fallback logic
    if '!res.contains_key("custom-rendezvous-server")' not in text:
        old_get_opts = """    pub fn get_options() -> HashMap<String, String> {
        let mut res = DEFAULT_SETTINGS.read().unwrap().clone();
        res.extend(CONFIG2.read().unwrap().options.clone());
        res.extend(OVERWRITE_SETTINGS.read().unwrap().clone());
        res
    }"""
        new_get_opts = """    pub fn get_options() -> HashMap<String, String> {
        let mut res = DEFAULT_SETTINGS.read().unwrap().clone();
        res.extend(CONFIG2.read().unwrap().options.clone());
        res.extend(OVERWRITE_SETTINGS.read().unwrap().clone());
        if !res.contains_key("custom-rendezvous-server") || res["custom-rendezvous-server"].is_empty() {
            if let Some(first) = RENDEZVOUS_SERVERS.first() {
                if !first.is_empty() {
                    res.insert("custom-rendezvous-server".to_string(), first.to_string());
                }
            }
        }
        if !res.contains_key("key") || res["key"].is_empty() {
            if !RS_PUB_KEY.is_empty() {
                res.insert("key".to_string(), RS_PUB_KEY.to_string());
            }
        }
        if !res.contains_key("relay-server") || res["relay-server"].is_empty() {
            if !RELAY_SERVER.is_empty() {
                res.insert("relay-server".to_string(), RELAY_SERVER.to_string());
            }
        }
        if !res.contains_key("api-server") || res["api-server"].is_empty() {
            if !API_SERVER.is_empty() {
                res.insert("api-server".to_string(), API_SERVER.to_string());
            }
        }
        res
    }"""
        text = text.replace(old_get_opts, new_get_opts)

    if 'match k {' not in text:
        old_get_opt = """    pub fn get_option(k: &str) -> String {
        get_or(
            &OVERWRITE_SETTINGS,
            &CONFIG2.read().unwrap().options,
            &DEFAULT_SETTINGS,
            k,
        )
        .unwrap_or_default()
    }"""
        new_get_opt = """    pub fn get_option(k: &str) -> String {
        let v = get_or(
            &OVERWRITE_SETTINGS,
            &CONFIG2.read().unwrap().options,
            &DEFAULT_SETTINGS,
            k,
        )
        .unwrap_or_default();
        if v.is_empty() {
            match k {
                "custom-rendezvous-server" => {
                    RENDEZVOUS_SERVERS.first().map(|s| s.to_string()).unwrap_or_default()
                }
                "key" => RS_PUB_KEY.to_string(),
                "relay-server" => RELAY_SERVER.to_string(),
                "api-server" => API_SERVER.to_string(),
                _ => v,
            }
        } else {
            v
        }
    }"""
        text = text.replace(old_get_opt, new_get_opt)

    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("[CI] Custom server and branding successfully injected into config.rs!")

    # 2. Patch Flutter server settings dialog
    dialog_path = os.path.join("flutter", "lib", "mobile", "widgets", "dialog.dart")
    patch_dialog_file(dialog_path)

    # 3. Patch About page website link and policy
    sp_path = os.path.join("flutter", "lib", "desktop", "pages", "desktop_setting_page.dart")
    patch_about_page(sp_path)

if __name__ == "__main__":
    main()
