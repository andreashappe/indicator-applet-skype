#!/usr/bin/env python
#
#Copyright 2010 Andreas Happe
#
#Authors:
#    Andreas Happe <andreashappe@snikt.net>
#
#This program is free software: you can redistribute it and/or modify it 
#under the terms of either or both of the following licenses:
#
#1) the GNU Lesser General Public License version 3, as published by the 
#Free Software Foundation; and/or
#2) the GNU Lesser General Public License version 2.1, as published by 
#the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the applicable version of the GNU Lesser General Public 
#License for more details.
#
#You should have received a copy of both the GNU Lesser General Public 
#License version 3 and version 2.1 along with this program.  If not, see 
#<http://www.gnu.org/licenses/>
#


# Documentation:
# just start it

import indicate
import gobject
import gtk
import Skype4Py

from time import time

name_sender = {}

def display(indicator):
    global name_sender

    display_name = indicator.get_property("name")
    skype_name = name_sender[display_name].Handle
    skype.Client.OpenMessageDialog(skype_name);

def server_display(server):
    skype.Client.Focus();

def OnAttach(status):
    if status == Skype4Py.apiAttachAvailable:
        skype.Attach();

    if status == Skype4Py.apiAttachSuccess:
        print 'connected to skype!'

def timeout_check(server):
    print "timeout?\n"

    unread = {}
    global name_sender

    for mesg in skype.MissedMessages:
        # TODO am I overwriting the timestamp? shouldn't I just use the last one?
        unread[mesg.FromDisplayName] = mesg.Timestamp

    for key in unread:
        add_notification(key, mesg.Sender, unread[key])

    return True

def do_nothing(indicator):
    True

def add_notification(display_name, Sender, timestamp):
    global name_sender

    print "adding " + display_name

    indicator = indicate.Indicator()
    indicator.set_property("name", display_name)
    name_sender[display_name] = Sender
    indicator.set_property_time("time", timestamp)
    indicator.set_property('draw-attention', 'true');
    indicator.connect("user-display", display)
    indicator.show()

    # TODO: why?
    gobject.timeout_add_seconds(5, do_nothing, indicator)

# this is needed, cause otherwise the skype menu is only showed
# when there are new unread messages.. another workaround
def workaround_show_skype():
  indicator = indicate.Indicator()
  indicator.set_property("name", "workaround..")
  indicator.connect("user-display", display)
  indicator.show()
  indicator.hide()
    

def OnMessageStatus(Message, Status):
    print 'message status\n'

    if Status == 'RECEIVED':
        print(Message.FromDisplayName + "sent a message")
        add_notification(Message.FromDisplayName, Message.Sender, Message.Timestamp)

if __name__ == "__main__":
    server = indicate.indicate_server_ref_default()
    server.set_type("message.im")
    server.set_desktop_file("/usr/share/applications/skype.desktop")
    server.connect("server-display", server_display)

    workaround_show_skype()

    # why is this needed?
    gobject.timeout_add_seconds(5, timeout_check, server)

    # initialize skype
    skype = Skype4Py.Skype();
    skype.OnAttachmentStatus = OnAttach;
    skype.OnMessageStatus = OnMessageStatus; 
    skype.Attach();

    # check for newly unread messages..
    timeout_check(server)

    gtk.main()
