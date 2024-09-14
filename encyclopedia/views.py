from random import randint
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django import forms
from markdown2 import Markdown
from django.core.files.storage import default_storage
from . import util
from django.core.validators import RegexValidator


class NewEntFm(forms.Form):
    title = forms.CharField(label="Enter a title", max_length=30,
                            widget=forms.TextInput(
                                attrs={'class': 'form-control mb-4'}),
                            validators=[RegexValidator('^[a-zA-Z0-9 -]{1,30}$',)])
    content = forms.CharField(
        required=True,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-4",
                "placeholder": "Content (markdown)",
                "id": "new_content",
            }
        ),
    )


def index(request):
    return render(
        request, "encyclopedia/index.html", {"entries": util.list_entries()}
    )


def wiki(request, entry):
    if entry not in util.list_entries():
        raise Http404
    content = util.get_entry(entry)
    return render(
        request,
        "encyclopedia/wiki.html",
        {"title": entry, "content": Markdown().convert(content)},
    )


def search(request):
    query = request.GET.get("q", "")
    if query is None or query == "Enter your title or text for search:":
        return render(
            request,
            "encyclopedia/search.html",
            {"found_entries": "", "query": query},
        )

    entries = util.list_entries()

    found_entries = [
        valid_entry
        for valid_entry in entries
        if query.lower() in valid_entry.lower()
    ]
    if len(found_entries) == 1:
        return redirect("wiki", found_entries[0])

    return render(
        request,
        "encyclopedia/search.html",
        {"found_entries": found_entries, "query": query},
    )


def new(request):
    
    if request.method == "GET":
        return render(request, "encyclopedia/new.html", {
            "form": NewEntFm()
        })
    if request.method == "POST":
        form = NewEntFm(request.POST)
        if not form.is_valid():
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
        title = form.cleaned_data["title"]
        content = form.cleaned_data["content"]

        filename = f"entries/{title}.md"
        if default_storage.exists(filename):
            messages.add_message(request, messages.ERROR,
                                 'Entry already exists with the provided title!')
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
        else:
            util.save_entry(title, content)
            return redirect("wiki", title)


def random_entry(request):
    entries = util.list_entries()
    entry = entries[randint(0, len(entries) - 1)]
    return redirect("wiki", entry)


def edit(request, entry):
    if request.method == "GET":
        title = entry
        content = util.get_entry(title)
        form = NewEntFm({"title": title, "content": content})
        return render(
            request,
            "encyclopedia/edit.html",
            {"form": form, "title": title},
        )

    form = NewEntFm(request.POST)
    if form.is_valid():
        title = form.cleaned_data.get("title")
        content = form.cleaned_data.get("content")

        util.save_entry(title=title, content=content)
        return redirect("wiki", title)


def handler404(request, *args):
    return render(request, "Error.html", {})
