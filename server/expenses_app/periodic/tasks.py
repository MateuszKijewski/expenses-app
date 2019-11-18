from core.models import ReccuringPayment

from celery import task


@task(name='periodic')
def set_periodics_payments():
    """Sets payment as paid if it was supposed to be paid until today"""
    payments = ReccuringPayment.objects.all()
    today_payments_ids = [
        payment.id
        for payment in payments
        if type(payment.until_payment()) != int
    ]
    print(today_payments_ids)
    today_payments = ReccuringPayment.objects.filter(pk__in=today_payments_ids)
    for payment in today_payments:
        payment.paid = False
        print("It works!")
        payment.save()