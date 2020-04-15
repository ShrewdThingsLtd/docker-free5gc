#!/bin/bash

go test -v registration_test.go n3_setup_test.go ngsetup_test.go -run TestRegistration
#go test -v dataplane_test.go -run TestRegistration
