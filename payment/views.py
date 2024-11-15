from django.shortcuts import render, redirect
import razorpay
from django.conf import settings
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest

# Authorize Razorpay Client with API Keys
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

class Donate(TemplateView):
    template_name = 'payment/index.html'

    def get(self, request):
        print("======= GET Request =========")
        currency = 'INR'
        amount = 10000  # Rs. 100

        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        callback_url = 'http://127.0.0.1:8000/payment/handler/'

        # we need to pass these details to frontend.
        context = {}
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url

        return render(request, self.template_name, context=context)

# we need to csrf_exempt this url as POST request will be made by Razorpay and 
# it won't have the csrf token
@csrf_exempt
def handler(request):
    print("======= Handler =========")
    # only accept POST request.
    if request.method == "POST":
        print("======= POST Request =========")
        try:
            print("======= try 1 =========")
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print("=========== Result : ", result, " ==========")
            if result is not None:
                amount = 10000
                try:
                    print("======= try 2 =========")
                    # capture the payment
                    razorpay_client.payment.capture(payment_id, amount)
                    
                    # render success page on successful capture of payment
                    return render(request, 'payment/success.html')
                except:
                    print("======= except 2 =========")
                    # if there is an error while capturing payment.
                    return render(request, 'payment/failure.html')
            else:
                print("======= signature verification fail =========")
                # if signature verification fails.
                return render(request, 'payment/failure.html')
        except:
            print("======= except 1 =========")
            # if we don't find the required parameters in POST data
            # return HttpResponseBadRequest()
            return render(request, 'payment/failure.html')
        
    else:
        print("other thank POST Request")
        # if other than POST request is made.
        # return HttpResponseBadRequest()
        return render(request, 'payment/failure.html')