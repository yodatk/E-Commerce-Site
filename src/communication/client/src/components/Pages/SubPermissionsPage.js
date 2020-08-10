import React, {Component} from "react";
import {MDBBadge, MDBBtn, MDBContainer, MDBLink, MDBTable, MDBTableBody, MDBTableHead} from "mdbreact";
import axios from "axios";
import {Button} from "semantic-ui-react";
import {Redirect, withRouter} from "react-router-dom";

export class SubPermissionsPage extends Component {
    state = {
        permissions: []
    }

    componentDidMount() {
        axios.get(
            `/fetch_all_sub_staff/${this.props.getUserId()}/${this.props.match.params.store_name}`)
            .then((res) => {
                this.setState({permissions: (res.data !== null && 'data' in res.data) ? res.data.data : []})
            }).catch(error => {
            console.log(error)
        });
    }

    render() {
        return (
            <MDBContainer>
                <MDBTable>
                    <MDBTableHead color="primary-color" textWhite>
                        <tr>
                            <th>#</th>
                            <th>Username</th>
                            <th>Role</th>
                            <th>Edit</th>
                        </tr>
                    </MDBTableHead>
                    <MDBTableBody>
                        {this.state.permissions.map((perm, i) => (
                            <tr key={i}>
                                <td>{i}</td>
                                <td>{perm.user}</td>
                                <td>{perm.role}</td>
                                <td><MDBLink key={`${perm.user}_${perm.store_name}_${i}`}
                                             to={`/edit_staff_page/${perm.store_name}/${perm.user}/${perm.appointed_by}/${perm.can_manage_inventory}/${perm.can_manage_discount}/${perm.open_and_close_store}/${perm.watch_purchase_history}/${perm.appoint_new_store_manager}/${perm.appoint_new_store_owner}`}><MDBBtn
                                    color='orange'>Edit</MDBBtn></MDBLink></td>
                            </tr>
                        ))}
                    </MDBTableBody>
                </MDBTable>
            </MDBContainer>
        );
    }
}

export default withRouter(SubPermissionsPage);