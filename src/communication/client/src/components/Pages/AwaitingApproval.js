import React, {Component} from "react";
import {MDBBtn, MDBContainer, MDBLink, MDBTable, MDBTableBody, MDBTableHead} from "mdbreact";
import axios from "axios";
import {Redirect, withRouter} from "react-router-dom";

export class AwaitingApproval extends Component {
    state = {
        awaiting_approvals: []
    }

    componentDidMount() {
        axios.get(
            "/fetch_awaiting_approvals/" + this.props.getUserId() + "/" + this.props.match.params.storename)
            .then((res) => {
                console.log(res)
                if (res.data) {
                    this.setState({awaiting_approvals: res.data.awaiting_approvals})
                }
            }).catch(error => {
            console.log(error)
        });
    }

    approve(username) {
        if (window.confirm("Are you sure you wish to approve this owner")) {
            axios.post(
            "/approve_new_owner",{'user_id': this.props.getUserId(), 'username': username, 'storename': this.props.match.params.storename})
            .then((res) => {
                console.log(res)
                this.setState({redirectAfterRegistered: "/store_page/" + this.props.match.params.storename})
            }).catch(error => {
            console.log(error)
        });
        }
    }


    deny(username) {
        if (window.confirm("Are you sure you wish to deny this owner")) {
            axios.post(
            "/deny_new_owner",{'user_id': this.props.getUserId(), 'username': username, 'storename': this.props.match.params.storename})
            .then((res) => {
                console.log(res)
                this.setState({redirectAfterRegistered: "/store_page/" + this.props.match.params.storename})
            }).catch(error => {
            console.log(error)
        });
        }
    }

    render() {
        if (this.state.redirectAfterRegistered) {
            return <Redirect to={this.state.redirectAfterRegistered}/>
        }
        else {
            return (
                <MDBContainer>
                    <MDBTable>
                        <MDBTableHead color="primary-color" textWhite>
                            <tr>
                                <th>#</th>
                                <th>Username suggested</th>
                                <th>Pending</th>
                                <th>Approved</th>
                                <th>Approve</th>
                                <th>Deny</th>
                            </tr>
                        </MDBTableHead>
                        <MDBTableBody>
                            {this.state.awaiting_approvals.map((app, i) => (
                                <tr key={i}>
                                    <td>{i + 1}</td>
                                    <td>{app.username}</td>
                                    <td>{app.pending}</td>
                                    <td>{app.approved}</td>
                                    <td><MDBBtn onClick={() => this.approve(app.username)}>Approve</MDBBtn></td>
                                    <td><MDBBtn onClick={() => this.deny(app.username)}>Deny</MDBBtn></td>
                                </tr>
                            ))}
                        </MDBTableBody>
                    </MDBTable>


                </MDBContainer>
            );
        }
    }
}

export default withRouter(AwaitingApproval);
