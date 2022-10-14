#!/bin/bash
# SPDX-FileCopyrightText: © 2022 ELABIT GmbH <mail@elabit.de>
# SPDX-License-Identifier: GPL-3.0-or-later


echo "+ Generating CMK devcontainer file ..."
# Ref LeP3qq
envsubst < .devcontainer/devcontainer_tpl.json > .devcontainer/devcontainer.json
# devcontainer.json contains a VS Code Variable ${containerWorkspaceFolder}, which would also 
# be processed by envsubst. To avoid this, the template files contain ###{containerWorkspaceFolder}.
# The three hashes are replaced with $ _after_ envsusbt has done its work. 
# Mac-only sed... 
sed -i "" 's/###/$/' .devcontainer/devcontainer.json

echo ">>> Preparation for Checkmk version $VERSION finished."
echo "You can now start the devcontainer in VS Code with 'Remote-Containers: Rebuild Container'."