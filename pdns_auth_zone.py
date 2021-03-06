#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Kevin P. Fleming <kevin@km6g.us>
# Apache License 2.0 (see LICENSE)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
%YAML 1.2
---
module: pdns_auth_zone

short_description: Manages a zone in a PowerDNS Authoritative server

description:
  - This module allows a task to manage the presence and configuration
    of a zone in a PowerDNS Authoritative server.

requirements:
  - bravado

options:
  state:
    description:
      - If C(present) the zone will be created if necessary; if it
        already exists, its configuration will be updated to match
        the provided properties.
      - If C(absent) the zone will be removed it if exists.
      - If C(exists) the zone's existence will be checked, but it
        will not be modified. Any configuration properties provided
        will be ignored.
      - If C(notify) and the zone kind is C(Master), then NOTIFY
        will be sent to the zone's slaves.
      - If C(notify) and the zone kind is C(Slave), then the slave
        zone will be updated as if a NOTIFY had been received.
      - If C(retrieve) and the zone kind is C(Slave), then the slave
        zone will be retrieved from the master.
    choices: [ 'present', 'absent', 'exists', 'notify', 'retrieve' ]
    type: str
    required: false
    default: 'present'
  name:
    description:
      - Name of the zone to be managed.
    type: str
    required: true
  server_id:
    description:
      - ID of the server instance which holds the zone.
    type: str
    required: false
    default: 'localhost'
  api_url:
    description:
      - URL of the API endpoint in the server.
    type: str
    required: false
    default: 'http://localhost:8081'
  api_key:
    description:
      - Key (token) used to authenticate to the API endpoint in the server.
    type: str
    required: true
  api_spec_file:
    description:
      - Path to a file containing the OpenAPI (Swagger) specification for the
        API version implemented by the server.
    type: path
    required: true
  properties:
    description:
      - Zone properties. Ignored when I(state=exists), I(state=absent), I(state=notify), or I(state=retrieve).
    type: complex
    contains:
      kind:
        description:
          - Zone kind.
        choices: [ 'Native', 'Master', 'Slave' ]
        type: str
        required: true
      account:
        description:
          - Optional string used for local policy.
        type: str
      nameservers:
        description:
          - List of nameserver names listed in SOA record for zone.
            Only used when I(kind=Native) or I(kind=Master).
        type: list
        elements: str
      masters:
        description:
          - List of IPv4 or IPv6 addresses which are masters for this zone.
            Only used when I(kind=Slave).
        type: list
        elements: str
  metadata:
    description:
      - Zone metadata. Ignored when I(state=exists), I(state=absent), I(state=notify), or I(state=retrieve).
    type: complex
    contains:
      allow_axfr_from:
        description:
          - List of IPv4 and/or IPv6 subnets (or the special value AUTO-NS) from which AXFR requests will be accepted.
        type: list
        elements: str
      allow_dnsupdate_from:
        description:
          - List of IPv4 and/or IPv6 subnets from which DNSUPDATE requests will be accepted.
        type: list
        elements: str
      also_notify:
        description:
          - List of IPv4 and/or IPv6 addresses (with optional port numbers) which will receive NOTIFY for updates.
        type: list
        elements: str
      axfr_source:
        description:
          - IPv4 or IPv6 address to be used as the source address for AXFR and IXFR requests.
        type: str
      forward_dnsupdate:
        description:
          - Forward DNSUPDATE requests to one of the zone's masters.
        type: bool
      gss_acceptor_principal:
        description:
          - Kerberos/GSS principal which identifies this server.
        type: str
      gss_allow_axfr_principal:
        description:
          - Kerberos/GSS principal which must be included in AXFR requests.
        type: str
      ixfr:
        description:
          - Attempt IXFR when retrieving zone updates.
        type: bool
      notify_dnsupdate:
        description:
          - Send a NOTIFY to all slave servers after processing a DNSUPDATE request.
        type: bool
      publish_cdnskey:
        description:
          - Publish CDNSKEY records of the KSKs for the zone.
        type: bool
      publish_cds:
        description:
          - List of signature algorithm numbers for CDS records of the KSKs for the zone.
        type: list
        elements: str
      slave_renotify:
        description:
          - Re-send NOTIFY to slaves after receiving AXFR from master.
          - If this is not set, the 'slave-renotify' setting in the server configuration
            will be applied to the zone.
        type: bool
      soa_edit_dnsupdate:
        description:
          - Method to update the serial number in the SOA record after a DNSUPDATE.
        type: str
        choices: [ 'DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE' ]
        default: 'DEFAULT'
      tsig_allow_dnsupdate:
        description:
          - List of TSIG keys for which DNSUPDATE requests will be accepted.
        type: list
        elements: str

author:
  - Kevin P. Fleming (@kpfleming)
"""

EXAMPLES = """
%YAML 1.2
---
# create and populate a file which holds the API specification
- name: temp file to hold spec
  tempfile:
    state: file
    suffix: '.json'
    register: temp_file

- name: populate spec file
  copy:
    src: api-swagger.json
    dest: "{{ temp_file.path }}"

- name: check that zone exists
  pdns_auth_zone:
    name: d1.example.
    state: exists
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"

- name: check that zone exists on a non-default server
  pdns_auth_zone:
    name: d1.example.
    state: exists
    api_key: 'foobar'
    api_url: 'http://pdns.server.example:80'
    api_spec_file: "{{ temp_file.path }}"

- name: send NOTIFY to slave servers for zone
  pdns_auth_zone:
    name: d1.example.
    state: notify
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"

- name: retrieve zone from master server
  pdns_auth_zone:
    name: d1.example.
    state: retrieve
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"

- name: create native zone
  pdns_auth_zone:
    name: d2.example.
    state: present
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"
    properties:
      kind: 'Native'
      nameservers:
        - 'ns1.example.'
    metadata:
      allow_axfr_from: ['AUTO-NS']
      axfr_source: '127.0.0.1'

- name: change native zone to master
  pdns_auth_zone:
    name: d2.example.
    state: present
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"
    properties:
      kind: 'Master'

- name: delete zone
  pdns_auth_zone:
    name: d2.example.
    state: absent
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"

- name: create slave zone
  pdns_auth_zone:
    name: d3.example.
    state: present
    api_key: 'foobar'
    api_spec_file: "{{ temp_file.path }}"
    properties:
      kind: 'Slave'
      masters:
        - '1.1.1.1'
        - '::1'
"""

RETURN = """
%YAML 1.2
---
zone:
  description: Information about the zone
  returned: always
  type: complex
  contains:
    name:
      description: Name
      returned: always
      type: str
    exists:
      description: Indicate whether the zone exists
      returned: always
      type: bool
    kind:
      description: Kind
      returned: when present
      type: str
      choices: [ Native, Master, Slave ]
    serial:
      description: Serial number from SOA record
      returned: when present
      type: int
    dnssec:
      description: Flag indicating whether zone is signed with DNSSEC
      returned: when present
      type: bool
    masters:
      description: IP addresses of masters (only for slave zones)
      returned: when present
      type: list
      elements: str
    metadata:
      description: Zone metadata
      returned: when present
      type: complex
      contains:
        allow_axfr_from:
          description:
            - List of IPv4 and/or IPv6 subnets (or the special value AUTO-NS) from which AXFR requests will be accepted.
          type: list
          elements: str
        allow_dnsupdate_from:
          description:
            - List of IPv4 and/or IPv6 subnets from which DNSUPDATE requests will be accepted.
          type: list
          elements: str
        also_notify:
          description:
            - List of IPv4 and/or IPv6 addresses (with optional port numbers) which will receive NOTIFY for updates.
          type: list
          elements: str
        axfr_master_tsig:
          description:
            - Key to be used to AXFR the zone from its master.
          type: str
        axfr_source:
          description:
            - IPv4 or IPv6 address to be used as the source address for AXFR and IXFR requests.
          type: str
        forward_dnsupdate:
          description:
            - Forward DNSUPDATE requests to one of the zone's masters.
          type: bool
        gss_acceptor_principal:
          description:
            - Kerberos/GSS principal which identifies this server.
          type: str
        gss_allow_axfr_principal:
          description:
            - Kerberos/GSS principal which must be included in AXFR requests.
          type: str
        ixfr:
          description:
            - Attempt IXFR when retrieving zone updates.
          type: bool
        lua_axfr_script:
          description:
            - Script to be used to edit incoming AXFR requests; use 'NONE' to override a globally configured script.
          type: str
        notify_dnsupdate:
          description:
            - Send a NOTIFY to all slave servers after processing a DNSUPDATE request.
          type: bool
        publish_cdnskey:
          description:
            - Publish CDNSKEY records of the KSKs for the zone.
          type: bool
        publish_cds:
          description:
            - List of signature algorithm numbers for CDS records of the KSKs for the zone.
          type: list
          elements: str
        slave_renotify:
          description:
            - Re-send NOTIFY to slaves after receiving AXFR from master.
          type: bool
        soa_edit_dnsupdate:
          description:
            - Method to update the serial number in the SOA record after a DNSUPDATE.
          type: str
          choices: [ 'DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE' ]
          default: 'DEFAULT'
        tsig_allow_axfr:
          description:
            - List of TSIG keys for which AXFR requests will be accepted.
          type: list
          elements: str
        tsig_allow_dnsupdate:
          description:
            - List of TSIG keys for which DNSUPDATE requests will be accepted.
          type: list
          elements: str
"""

from ansible.module_utils.basic import AnsibleModule

from urllib.parse import urlparse


class APIZonesWrapper(object):
    def __init__(self, raw_api, server_id, zone_id):
        self.raw_api = raw_api
        self.server_id = server_id
        self.zone_id = zone_id

    def axfrRetrieveZone(self):
        return self.raw_api.axfrRetrieveZone(
            server_id=self.server_id, zone_id=self.zone_id
        ).result()

    def createZone(self, **kwargs):
        return self.raw_api.createZone(server_id=self.server_id, **kwargs).result()

    def deleteZone(self):
        return self.raw_api.deleteZone(
            server_id=self.server_id, zone_id=self.zone_id
        ).result()

    def listZone(self):
        return self.raw_api.listZone(
            server_id=self.server_id, zone_id=self.zone_id
        ).result()

    def listZones(self, **kwargs):
        return self.raw_api.listZones(server_id=self.server_id, **kwargs).result()

    def notifyZone(self):
        return self.raw_api.notifyZone(
            server_id=self.server_id, zone_id=self.zone_id
        ).result()

    def putZone(self, **kwargs):
        return self.raw_api.putZone(
            server_id=self.server_id, zone_id=self.zone_id, **kwargs
        ).result()


class APIZoneMetadataWrapper(object):
    def __init__(self, raw_api, server_id, zone_id):
        self.raw_api = raw_api
        self.server_id = server_id
        self.zone_id = zone_id

    def deleteMetadata(self, **kwargs):
        return self.raw_api.deleteMetadata(
            server_id=self.server_id, zone_id=self.zone_id, **kwargs
        ).result()

    def listMetadata(self):
        return self.raw_api.listMetadata(
            server_id=self.server_id, zone_id=self.zone_id
        ).result()

    def modifyMetadata(self, **kwargs):
        return self.raw_api.modifyMetadata(
            server_id=self.server_id, zone_id=self.zone_id, **kwargs
        ).result()


class APIWrapper(object):
    def __init__(self, raw_api, server_id, zone_id):
        self.zones = APIZonesWrapper(raw_api.zones, server_id, zone_id)
        self.zonemetadata = APIZoneMetadataWrapper(
            raw_api.zonemetadata, server_id, zone_id
        )

    def setZoneID(self, zone_id):
        self.zones.zone_id = zone_id
        self.zonemetadata.zone_id = zone_id


class Metadata(object):
    map_by_kind = {}
    map_by_meta = {}

    def __init__(self, kind):
        self.kind = kind
        self.meta = kind.lower().replace("-", "_")
        self.map_by_kind[self.kind] = self
        self.map_by_meta[self.meta] = self

    @classmethod
    def by_kind(cls, kind):
        return cls.map_by_kind.get(kind)

    @classmethod
    def by_meta(cls, meta):
        return cls.map_by_meta.get(meta)

    @classmethod
    def meta_defaults(cls):
        return {k: v.default() for k, v in cls.map_by_meta.items()}

    @classmethod
    def set_all(cls, metadata, api):
        for meta, value in metadata.items():
            m = cls.by_meta(meta)
            if m:
                m.set(value or m.default(), api)

    @classmethod
    def update_all(cls, old, new, api):
        changed = False

        for k, v in cls.map_by_meta.items():
            if v.update(old.get(k), new.get(k) or v.default(), api):
                changed = True

        return changed


class MetadataBinaryValue(Metadata):
    def default(self):
        return False

    def result_from_api(self, res, api):
        res[self.meta] = api["metadata"][0] == "1"

    def set(self, value, api):
        if value:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": ["1"]}
            )

    def update(self, oldval, newval, api):
        if newval == oldval:
            return False

        if newval:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": ["1"]}
            )
        else:
            api.zonemetadata.deleteMetadata(metadata_kind=self.kind)
        return True


class MetadataBinaryPresence(Metadata):
    def default(self):
        return False

    def result_from_api(self, res, api):
        res[self.meta] = True

    def set(self, value, api):
        if value:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": [""]}
            )

    def update(self, oldval, newval, api):
        if newval == oldval:
            return False

        if newval:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": [""]}
            )
        else:
            api.zonemetadata.deleteMetadata(metadata_kind=self.kind)
        return True


class MetadataTernaryValue(Metadata):
    def default(self):
        return None

    def result_from_api(self, res, api):
        res[self.meta] = api["metadata"][0] == "1"

    def set(self, value, api):
        if value is not None:
            if value:
                api.zonemetadata.modifyMetadata(
                    metadata_kind=self.kind, metadata={"metadata": ["1"]}
                )
            else:
                api.zonemetadata.modifyMetadata(
                    metadata_kind=self.kind, metadata={"metadata": ["0"]}
                )

    def update(self, oldval, newval, api):
        if newval == oldval:
            return False

        if newval is not None:
            if newval:
                api.zonemetadata.modifyMetadata(
                    metadata_kind=self.kind, metadata={"metadata": ["1"]}
                )
            else:
                api.zonemetadata.modifyMetadata(
                    metadata_kind=self.kind, metadata={"metadata": ["0"]}
                )
        else:
            api.zonemetadata.deleteMetadata(metadata_kind=self.kind)
        return True


class MetadataListValue(Metadata):
    def default(self):
        return []

    def result_from_api(self, res, api):
        res[self.meta] = api["metadata"]

    def set(self, value, api):
        if len(value) != 0:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": value}
            )

    def update(self, oldval, newval, api):
        if newval == oldval:
            return False

        if len(newval) != 0:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": newval}
            )
        else:
            api.zonemetadata.deleteMetadata(metadata_kind=self.kind)
        return True


class MetadataStringValue(Metadata):
    def default(self):
        return ""

    def result_from_api(self, res, api):
        res[self.meta] = api["metadata"][0]

    def set(self, value, api):
        if value:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": [value]}
            )

    def update(self, oldval, newval, api):
        if newval == oldval:
            return False

        if len(newval) != 0:
            api.zonemetadata.modifyMetadata(
                metadata_kind=self.kind, metadata={"metadata": [newval]}
            )
        else:
            api.zonemetadata.deleteMetadata(metadata_kind=self.kind)
        return True


MetadataListValue("ALLOW-AXFR-FROM")
MetadataListValue("ALLOW-DNSUPDATE-FROM")
MetadataListValue("ALSO-NOTIFY")
MetadataStringValue("AXFR-SOURCE")
MetadataBinaryPresence("FORWARD-DNSUPDATE")
MetadataStringValue("GSS-ACCEPTOR-PRINCIPAL")
MetadataStringValue("GSS-ALLOW-AXFR-PRINCIPAL")
MetadataBinaryValue("IXFR")
MetadataBinaryValue("NOTIFY-DNSUPDATE")
MetadataBinaryValue("PUBLISH-CDNSKEY")
MetadataListValue("PUBLISH-CDS")
MetadataTernaryValue("SLAVE-RENOTIFY")
MetadataStringValue("SOA-EDIT-DNSUPDATE")
MetadataListValue("TSIG-ALLOW-DNSUPDATE")


def build_zone_result(api):
    z = {}
    zone_info = api.zones.listZone()
    z["exists"] = True
    z["name"] = zone_info["name"]
    z["kind"] = zone_info["kind"]
    z["serial"] = zone_info["serial"]
    z["account"] = zone_info["account"]
    z["dnssec"] = zone_info["dnssec"]
    z["masters"] = zone_info["masters"]
    # initialize the metadata result dict
    z["metadata"] = Metadata.meta_defaults()
    z["metadata"]["api_rectify"] = zone_info["api_rectify"]
    z["metadata"]["nsec3narrow"] = zone_info["nsec3narrow"]
    z["metadata"]["nsec3param"] = zone_info["nsec3param"]
    z["metadata"]["soa_edit"] = zone_info["soa_edit"]
    z["metadata"]["soa_edit_api"] = zone_info["soa_edit_api"]

    zone_meta = api.zonemetadata.listMetadata()
    for m in zone_meta:
        o = Metadata.by_kind(m["kind"])
        if o:
            o.result_from_api(z["metadata"], m)

    return zone_info, z


def main():
    module_args = {
        "state": {
            "type": "str",
            "default": "present",
            "choices": ["present", "absent", "exists", "notify", "retrieve"],
        },
        "name": {"type": "str", "required": True,},
        "server_id": {"type": "str", "default": "localhost",},
        "api_url": {"type": "str", "default": "http://localhost:8081",},
        "api_key": {"type": "str", "required": True, "no_log": True,},
        "api_spec_file": {"type": "path", "required": True,},
        "properties": {
            "type": "dict",
            "options": {
                "kind": {
                    "type": "str",
                    "choices": ["Native", "Master", "Slave"],
                    "required": True,
                },
                "account": {"type": "str",},
                "nameservers": {"type": "list", "elements": "str",},
                "masters": {"type": "list", "elements": "str",},
            },
        },
        "metadata": {
            "type": "dict",
            "options": {
                "allow_axfr_from": {"type": "list", "elements": "str",},
                "allow_dnsupdate_from": {"type": "list", "elements": "str",},
                "also_notify": {"type": "list", "elements": "str",},
                "axfr_source": {"type": "str",},
                "forward_dnsupdate": {"type": "bool",},
                "gss_acceptor_principal": {"type": "str",},
                "gss_allow_axfr_principal": {"type": "str",},
                "ixfr": {"type": "bool",},
                "notify_dnsupdate": {"type": "bool",},
                "publish_cndskey": {"type": "bool",},
                "publish_cds": {"type": "list", "elements": "str",},
                "slave_renotify": {"type": "bool",},
                "soa_edit_dnsupdate": {
                    "type": "str",
                    "default": "DEFAULT",
                    "choices": [
                        "DEFAULT",
                        "INCREASE",
                        "EPOCH",
                        "SOA-EDIT",
                        "SOA-EDIT-INCREASE",
                    ],
                },
                "tsig_allow_dnsupdate": {"type": "list", "elements": "str",},
            },
        },
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    try:
        from bravado.requests_client import RequestsClient
        from bravado.client import SwaggerClient
        from bravado.swagger_model import load_file
    except ImportError:
        module.fail_json(
            msg="The pdns_auth_zone module requires the 'bravado' package."
        )

    result = {
        "changed": False,
    }

    state = module.params["state"]
    server_id = module.params["server_id"]
    zone = module.params["name"]

    if module.check_mode:
        module.exit_json(**result)

    url = urlparse(module.params["api_url"])

    http_client = RequestsClient()
    http_client.set_api_key(
        url.netloc, module.params["api_key"], param_name="X-API-Key", param_in="header"
    )

    spec = load_file(module.params["api_spec_file"])
    spec["host"] = url.netloc
    spec["schemes"] = [url.scheme]

    raw_api = SwaggerClient.from_spec(spec, http_client=http_client)

    # create an APIWrapper to proxy the raw_api object
    # and curry the server_id and zone_id into all API
    # calls automatically
    api = APIWrapper(raw_api, server_id, None)

    result["zone"] = {}
    result["zone"]["name"] = zone
    result["zone"]["exists"] = False

    # first step is to get information about the zone, if it exists
    # this is required to translate the user-friendly zone name into
    # the zone_id required for subsequent API calls

    partial_zone_info = api.zones.listZones(zone=zone)

    if len(partial_zone_info) == 0:
        if (state == "exists") or (state == "absent"):
            # exit as there is nothing left to do
            module.exit_json(**result)
        elif state == "notify":
            module.fail_json(
                msg="NOTIFY cannot be requested for a non-existent zone", **result
            )
        elif state == "retrieve":
            module.fail_json(
                msg="Retrieval cannot be requested for a non-existent zone", **result
            )
        else:
            # state must be 'present'
            zone_id = None
    else:
        #
        # get the full zone info and populate the result dict
        zone_id = partial_zone_info[0]["id"]
        api.setZoneID(zone_id)
        zone_info, result["zone"] = build_zone_result(api)

    # if only an existence check was requested,
    # the operation is complete
    if state == "exists":
        module.exit_json(**result)

    # if absence was requested, remove the zone and exit
    if state == "absent":
        api.zones.deleteZone()
        result["changed"] = True
        module.exit_json(**result)

    # if NOTIFY was requested, process it and exit
    if state == "notify":
        if zone_info["kind"] == "Native":
            module.fail_json(
                msg="NOTIFY cannot be requested for 'Native' zones", **result
            )

        api.zones.notifyZone()
        result["changed"] = True
        module.exit_json(**result)

    # if retrieval was requested, process it and exit
    if state == "retrieve":
        if zone_info["kind"] != "Slave":
            module.fail_json(
                msg="Retrieval can only be requested for 'Slave' zones", **result
            )

        api.zones.axfrRetrieveZone()
        result["changed"] = True
        module.exit_json(**result)

    # state must be 'present'
    if not zone_id:
        # create the requested zone
        zone_struct = {
            "name": zone,
        }

        if module.params["properties"]:
            props = module.params["properties"]

            if props["kind"]:
                zone_struct["kind"] = props["kind"]

                if props["kind"] != "Slave":
                    zone_struct["nameservers"] = props["nameservers"]

                if props["kind"] == "Slave":
                    zone_struct["masters"] = props["masters"]

            if props["account"]:
                zone_struct["account"] = props["account"]

        api.zones.createZone(rrsets=False, zone_struct=zone_struct)
        result["changed"] = True
        partial_zone_info = api.zones.listZones(zone=zone)
        api.setZoneID(partial_zone_info[0]["id"])

        if module.params["metadata"]:
            meta = module.params["metadata"]
            Metadata.set_all(meta, api)

        zone_info, result["zone"] = build_zone_result(api)
    else:
        # compare the zone's attributes to the provided
        # options and update it if necessary
        zone_struct = {}

        if module.params["properties"]:
            props = module.params["properties"]

            if props["kind"]:
                if zone_info["kind"] != props["kind"]:
                    zone_struct["kind"] = props["kind"]

                if props["kind"] == "Slave":
                    if props["masters"]:
                        mp_masters = props["masters"].sort()
                        zi_masters = zone_info["masters"].sort()

                        if zi_masters != mp_masters:
                            zone_struct["masters"] = props["masters"]

            if props["account"]:
                if zone_info["account"] != props["account"]:
                    zone_struct["account"] = props["account"]

        if len(zone_struct):
            api.zones.putZone(zone_struct=zone_struct)
            result["changed"] = True

        if module.params["metadata"]:
            old = result["zone"]["metadata"]
            new = module.params["metadata"]
            if Metadata.update_all(old, new, api):
                result["changed"] = True

        if result["changed"]:
            zone_info, result["zone"] = build_zone_result(api)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
