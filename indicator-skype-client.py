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

unread_messages = {}

# this is called, when somebody clicks upon one 'unread message'
# entry
def display(indicator):
    global name_sender
    global unread_messages

    display_name = indicator.get_property("name")
    skype_name = name_sender[display_name].Handle

    del unread_messages[display_name]
    skype.Client.OpenMessageDialog(skype_name);

# this is called when somebody clicks upon the 'skype' entry
def server_display(server):
    skype.Client.Focus();

def OnAttach(status):
    if status == Skype4Py.apiAttachAvailable:
        skype.Attach();

    if status == Skype4Py.apiAttachSuccess:
        print 'connected to skype!'

# update unread message collection
# TODO: also remove messages that have been read through skype, otherwise
#       they would stay until somebody clicks them in the indicator-applet
def timeout_check(server):
  global unread_messages

  print "timeout?\n"

  for mesg in skype.MissedMessages:
    if not mesg.FromDisplayName in unread_messages:
      unread_messages[mesg.FromDisplayName] = {}
      unread_messages[mesg.FromDisplayName]['count'] = 0

    # TODO am I overwriting the timestamp? shouldn't I just use the last one?
    # TODO 'ts' and 'count' are mutual exclusive? what is better?
    unread_messages[mesg.FromDisplayName]['ts'] = mesg.Timestamp
    unread_messages[mesg.FromDisplayName]['count'] += 1
    unread_messages[mesg.FromDisplayName]['sender'] = mesg.Sender

  for key in unread_messages:
    entry = unread_messages[key]
    add_notification(key, entry['sender'], entry['ts'], entry['count'])

  return True

def do_nothing(indicator):
    True

def add_notification(display_name, Sender, timestamp, count):
    global name_sender

    print "adding " + display_name

    try:
      # Ubuntu 9.10 and above
      indicator = indicate.Indicator()
    except:
      indicator = indicate.IndicatorMessage()

    indicator.set_property("name", display_name)
    name_sender[display_name] = Sender
    indicator.set_property("subtype", "instant")
    indicator.set_property('draw-attention', 'true');

    # we can only display timestamp OR count
    if count == 1:
      indicator.set_property_time("time", timestamp)
    else:
      indicator.set_property('count', str(count));
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
    

def OnMessageStatus(mesg, Status):
  global unread_messages

  print 'message status\n'

  if Status == 'RECEIVED':
    print(Message.FromDisplayName + "sent a message")
    if not mesg.FromDisplayName in unread_messages:
      unread_messages[mesg.FromDisplayName] = {}
      unread_messages[mesg.FromDisplayName]['count'] = 0
      unread_messages[mesg.FromDisplayName]['ts'] = mesg.Timestamp
    else:
      unread_messages[mesg.FromDisplayName]['count'] += 1

    add_notification(mesg.FromDisplayName, mesg.Sender, mesg.Timestamp, unread_messages[mesg.FromDisplayName]['count'])

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
