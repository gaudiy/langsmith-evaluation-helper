# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

# File for dataset creation

from langsmith import Client

client = Client()
print("client created")

toxic_examples = [
    ("Shut up, idiot", "Toxic", "test"),
    ("You're a wonderful person", "Not toxic", "test"),
    ("This is the worst thing ever", "Toxic", "test"),
    ("I had a great day today", "Not toxic", "train"),
    ("Nobody likes you", "Toxic", "train"),
    ("This movie is a masterpiece", "Not toxic", "train"),
    ("Go away and never come back", "Toxic", "train"),
    ("Thank you for your help", "Not toxic", "train"),
    ("This is so dumb", "Toxic", "train"),
    ("I appreciate your efforts", "Not toxic", "train"),
    ("This is a waste of time", "Toxic", "train"),
    ("This movie blows", "Toxic", "train"),
    ("This is unacceptable. I want to speak to the manager.", "Toxic", None),
]

toxic_dataset_name = "Toxic Queries Split"
if not client.has_dataset(dataset_name=toxic_dataset_name):
    toxic_dataset = client.create_dataset(dataset_name=toxic_dataset_name)
    inputs, outputs, splits = zip(
        *[({"text": text}, {"label": label}, splits) for text, label, splits in toxic_examples],
        strict=False,
    )
    client.create_examples(inputs=inputs, outputs=outputs, splits=list(splits), dataset_id=toxic_dataset.id)
