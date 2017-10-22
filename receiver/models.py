from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

import datetime


Base = declarative_base()


class ForwardingAddress(Base):
  __tablename__ = 'forwarding_address'
  id                        = Column(Integer, primary_key=True)
  callback                  = Column(String(255), nullable=False)
  destination_address       = Column(String(40), nullable=False )
  input_address             = Column(String(40), nullable=False, index=True)
  input_transaction_hash    = Column(String(255))
  transaction_hash          = Column(String(255))
  payee_addresses           = Column(Text)
  confirmations             = Column(Integer,nullable=False, default=0)
  value                     = Column(Integer)
  fwd_miners_fee            = Column(Integer)
  input_miners_fee          = Column(Integer)
  status                    = Column(Integer,nullable=False, default=0, index=True)
  signed_fwd_transaction    = Column(Text)
  created                   = Column(DateTime, default=datetime.datetime.now, nullable=False, index=True)
  transmitted               = Column(DateTime)
  is_confirmed_by_client    = Column(Boolean, nullable=False, default=False, index=True)
  confirm_callback_attempt  = Column(Integer,nullable=False, default=0)
  callback_number_of_errors = Column(Integer,nullable=False, default=0)

  def __repr__(self):
    return "<ForwardingAddress(id=%r, callback=%r, destination_address=%r, input_address=%r,input_transaction_hash=%r,"\
           "transaction_hash=%r, confirmations=%r, value=%r,fwd_miners_fee=%r, input_miners_fee=%r, status=%r, " \
           "is_confirmed_by_client=%r, signed_fwd_transaction=%r, payee_addresses=%r)>"\
    % (self.id, self.callback, self.destination_address, self.input_address, self.input_transaction_hash,
       self.transaction_hash, self.confirmations, self.value, self.fwd_miners_fee, self.input_miners_fee, self.status,
       self.is_confirmed_by_client, self.signed_fwd_transaction, self.payee_addresses)


  @staticmethod
  def create( session, destination_address, input_address, callback):
    rec = ForwardingAddress(callback = callback,destination_address = destination_address,input_address=input_address)
    session.add(rec)
    session.commit()
    return rec

  @staticmethod
  def get_by_id(session, id):
    return session.query(ForwardingAddress).filter_by(id=id).first()


  @staticmethod
  def get_by_input_address(session, input_address):
    return session.query(ForwardingAddress).filter_by(input_address=input_address).first()

  @staticmethod
  def get_unconfirmed_by_client(session):
    return session.query(ForwardingAddress).filter_by(is_confirmed_by_client=False).filter(ForwardingAddress.status > 0)

  def get_callback_url(self):
    from urlparse import urlparse, ParseResult
    import urllib

    callback_url_parse = urlparse(self.callback)
    query_args = {
      'fwd_fee'               : self.fwd_miners_fee or 0,
      'input_fee'             : self.input_miners_fee or 0,
      'value'                 : self.value,
      'input_address'         : self.input_address,
      'confirmations'         : self.confirmations,
      'transaction_hash'      : self.transaction_hash,
      'input_transaction_hash': self.input_transaction_hash,
      'destination_address'   : self.destination_address,
      'payee_addresses'       : self.payee_addresses
    }

    if not callback_url_parse.query:
      url_query = urllib.urlencode(query_args)
    else:
      url_query = callback_url_parse.query + '&' + urllib.urlencode(query_args)

    callback_url = ParseResult(scheme=callback_url_parse.scheme ,
                               netloc=callback_url_parse.netloc,
                               path=callback_url_parse.path,
                               params=callback_url_parse.params,
                               query= url_query,
                               fragment=callback_url_parse.fragment).geturl()

    return callback_url

  def set_as_completed(self, input_transaction_hash,transaction_hash,value,fwd_miners_fee,input_miners_fee,signed_fwd_transaction, payee_addresses = None):
    self.input_transaction_hash = input_transaction_hash
    self.transaction_hash       = transaction_hash
    self.value                  = value
    self.fwd_miners_fee         = fwd_miners_fee
    self.input_miners_fee       = input_miners_fee
    self.signed_fwd_transaction = signed_fwd_transaction
    self.payee_addresses        = payee_addresses
    self.status                 = 1


  def set_as_transmitted(self, transaction_hash=None):
    if transaction_hash:
      self.transaction_hash = transaction_hash
    self.transmitted = datetime.datetime.now()
    self.status  = 2

  def is_complete(self):
    return self.status >= 1


  def is_transmitted(self):
    return self.status >= 2


def db_bootstrap(session):
  pass



