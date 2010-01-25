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

unread_conversations = {}

# this is called, when somebody clicks upon one 'unread message'
# entry
def display(indicator):
    global unread_conversations

    # TODO move this into a class method?
    display_name = indicator.get_property("name")
    skype_name = UnreadConversation.skype_id_for(display_name)

    del unread_conversations[display_name]
    skype.Client.OpenMessageDialog(skype_name);

def do_nothing(indicator):
    True

class UnreadConversation:
  name_mappings = {}

  def __init__(self, display_name, timestamp, skype_id):
    self.display_name = display_name
    self.count = 0
    self.timestamps = [timestamp]
    UnreadConversation.name_mappings[self.display_name] = skype_id

  def add(self, timestamp):
    if not timestamp in self.timestamps:
      self.timestamps.add(timestamp)
      self.count += 1

  def skype_id_for(cls, display_name):
    return UnreadConversation.name_mappings[display_name]

  skype_id_for = classmethod(skype_id_for)

  def show(self):
    print "adding " + self.display_name

    try:
      # Ubuntu 9.10 and above
      indicator = indicate.Indicator()
    except:
      # Ubuntu 9.04
      indicator = indicate.IndicatorMessage()

    indicator.set_property("name", self.display_name)
    indicator.set_property("subtype", "instant")
    indicator.set_property('draw-attention', 'true');

    # we can only display timestamp OR count
    if self.count == 1:
      indicator.set_property_time("time", self.timestamp)
    else:
      indicator.set_property('count', str(self.count));
    indicator.connect("user-display", display)
    indicator.show()

    # TODO: why?
    gobject.timeout_add_seconds(5, do_nothing, indicator)

def add_message(mesg):
  global unread_conversations

  display_name = mesg.FromDisplayName

  if not display_name in unread_conversations:
    conversation = UnreadConversation(display_name, mesg.Timestamp, mesg.Sender.Handle)
    # TODO: should we do some sort of update for this?
    unread_conversations[display_name] = conversation
    unread_conversations[display_name].show()
  else:
    unread_conversations[display_name].add(mesg.Timestamp)
    unread_conversations[display_name].show()

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
  global unread_conversations
  print "timeout?\n"

  for mesg in skype.MissedMessages:
    add_message(mesg)

  return True

# this is needed, cause otherwise the skype menu is only showed
# when there are new unread messages.. another workaround
def workaround_show_skype():
  indicator = indicate.Indicator()
  indicator.set_property("name", "workaround..")
  indicator.connect("user-display", display)
  indicator.show()
  indicator.hide()
    

def OnMessageStatus(mesg, Status):
  global unread_conversations

  print 'message status\n'

  if Status == 'RECEIVED':
    print(Message.FromDisplayName + "sent a message")
    add_message(mesg)

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
