import random
import re
from typing import Type, Union, Optional

from pydantic import BaseModel

from fastiot.core.subject_helper import MSG_FORMAT_VERSION


class FastIoTData(BaseModel):
    """ Basemodel for all data types / data models to be transferred over the broker between the services.
    This is basically a Pydantic model with the additional handling of subjects. So any Pydantic model should work here,
    as long as it can be serialized using the library ``ormsgpack``.

    The subject is constructed from the model name, e.g. if your data model is called ``MySpecialModel`` a subject
    ``v1.my_special_subject`` will be created. If you want to have more control over the subject name you may overwrite
    the method :meth:`fastiot.core.data_models.FastIoTData.get_subject` in your data model or create a new model based
    on Pydantic’s :class:`pydantic.BaseModel`. See :ref:`publish-subscribe` for more details about publish and
    subscribe.

    For your own data models please use :class:`fastiot.core.data_models.FastIoTPublish` for data that is simply
    published over the broker. For Request and Response please use :class:`fastiot.core.data_models.FastIoTRequest` and
    :class:`fastiot.core.data_models.FastIoTResponse`.
    """

    @classmethod
    def _get_subject_name(cls, name: str):
        # Convert CamelCase to snake_case
        subject_name = f"{MSG_FORMAT_VERSION}.{re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()}"
        if name:
            subject_name += "." + name
        return subject_name


Msg = Union[FastIoTData, dict]
MsgCls = Type[Msg]


class FastIoTPublish(FastIoTData):
    """
    Base datatype for publishing data. Please refer to :ref:`tut-custom_data_types` for more information about creating
    your own data types.
    """
    @classmethod
    def get_subject(cls, name: str = "") -> "Subject":
        """
        This method returns the corresponding subject for the data model as :class:`fastiot.core.data_models.Subject`.

        :param name: The name of the subject. Please pay special attention to this parameter: The default is set to
                     ``""``. This works well for data models without hierarchies. In this case you will just subscribe
                     to ``v1.my_special_data_model``. If you use many sensors, like in the data model
                     :class:`fastiot.msg.ting.Thing` you have to provide a name. Then you can subscribe to
                     ``v1.thing.my_sensor``. If you want to subscribe to all sensors use ``*`` as name. See more in
                     :ref:`publish-subscribe`
        """
        return Subject(
            name=cls._get_subject_name(name=name),
            msg_cls=cls
        )


MsgPub = Union[FastIoTPublish, dict]
MsgClsPub = Type[MsgPub]


class FastIoTResponse(FastIoTData):
    """
    Base datatype for answering requests based on :class: `fastiot.core.data_models.FastIoTRequest`.
    Please refer to :ref:`tut-custom_data_types` for more information about creating your custom data types.
    """
    @classmethod
    def get_subject(cls):
        raise NotImplementedError("A response does not listen to any subjects, thus `get_subject()` is not "
                                  "implemented.")


MsgResp = Union[FastIoTResponse, dict]
MsgClsResp = Type[MsgResp]


class FastIoTRequest(FastIoTData):
    """
    Base datatype for handling requests. Please refer to :ref:`tut-custom_data_types` for more information about
    creating your own data types.
    """
    _reply_cls: Optional[Type[FastIoTResponse]] = None
    """
    This is the best way to describe the datatype (class) your request will be answered with. As an alternative you may
    manually define a :class:`fastiot.core.data_models.ReplySubject`.
    """
    @classmethod
    def get_reply_subject(cls, reply_cls: Optional["MsgCls"] = None, name: str = "") -> "ReplySubject":
        """
        This method returns the corresponding reply subject for the data model as
         :class:`fastiot.core.data_models.ReplySubject`.

        :param reply_cls: The corresponding reply class.
        :param name: The name of the subject. Please pay special attention to this parameter: The default is set to
                     ``""``. This works well for data models without hierarchies. In this case you will just subscribe
                     to ``v1.my_special_data_model``. If you use many sensors, like in the data model
                     :class:`fastiot.msg.ting.Thing` you have to provide a name. Then you can subscribe to
                     ``v1.thing.my_sensor``. If you want to subscribe to all sensors use ``*`` as name. See more in
                     :ref:`publish-subscribe`
        """
        if not reply_cls:
            reply_cls = cls._reply_cls
        if not reply_cls:
            raise TypeError("Reply class needs to be defined for class.")
        return ReplySubject(
            name=cls._get_subject_name(name=name),
            msg_cls=cls,
            reply_cls=reply_cls
        )


MsgReq = Union[FastIoTRequest, dict]
MsgClsReq = Type[MsgReq]


class Subject(BaseModel):
    """ General model to handle subjects for subscriptions within the framework. """

    name: str
    """ Name of the subject, s. :meth:`fastiot.core.data_models.FastIoTData.get_subject` for details about subscription
    names."""
    msg_cls: MsgCls
    """ Datatype the message will provide. """


class ReplySubject(Subject):
    """ Model for handle subject subscription which also have a reply to cls """

    reply_cls: MsgCls
    """ Set to a datatype, not the default ``None`` to expect a reply in this datatype. """

    def make_generic_reply_inbox(self) -> Subject:
        if self.reply_cls is None:
            raise ValueError("Cannot create generic inbox: reply_cls must not be none")

        return Subject(
            name='_INBOX' + str(random.randint(0, 1000000000)),
            msg_cls=self.reply_cls
        )

    def get_reply_inbox(self, reply_to: str) -> Subject:
        if self.reply_cls is None:
            raise ValueError("Expected reply_cls to be not None")

        return Subject(
            name=reply_to,
            msg_cls=self.reply_cls
        )
