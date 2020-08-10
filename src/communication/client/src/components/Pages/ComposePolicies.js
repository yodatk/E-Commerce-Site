import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBRow, MDBTable, MDBTableBody, MDBTableHead} from "mdbreact";
import axios from "axios";
import {Redirect, withRouter} from "react-router-dom";
import {CREATED, OK} from "http-status-codes";

export class ComposePolicies extends Component {
    state = {
        policies: [],
        redirectLink: null
    }
    selected = {}

    componentDidMount() {
        axios.get(
            "/fetch_policies/" + this.props.getUserId() + "/" + this.props.match.params.storename
        )
            .then((res) => {
                this.setState({policies: res.data !== null ? res.data.data : []});
            }).catch(error => {
            console.log(error)
        });
    }

    onChange = (e) => {
        this.selected[e.target.id] = e.target.checked
    };

    combine = (by_op) => {
        let included_ids = Object.keys(this.selected).filter(key => this.selected[key]).map(x => x.split('_')[1]);
        axios.post(
            "/combine_policies",
            {
                user_id: this.props.getUserId(),
                storename: this.props.match.params.storename,
                operator: by_op,
                policies_id_list: included_ids
            },
        )
            .then((res) => {
                console.log("combined policy created")
                console.log(res)
                if ((res.status === OK) || res.status === CREATED) {
                    this.setState({redirectLink: `/store_page/${this.props.match.params.storename}`})
                }
            }).catch(error => {
            console.log(error)
        });
    }

    render() {
        if (this.state.redirectLink !== null) {
            return <Redirect to={this.state.redirectLink}/>
        }
        return (
            <MDBContainer center>
                <MDBRow center>
                    <MDBCol center md="12">
                        <MDBBtn outline color="primary" onClick={() => this.combine('AND')}>AND</MDBBtn>
                        <MDBBtn outline onClick={() => this.combine('OR')}>OR</MDBBtn>
                        <MDBBtn outline color="secondary" onClick={() => this.combine('XOR')}>XOR</MDBBtn>
                    </MDBCol>
                </MDBRow>
                <MDBRow>
                    <MDBCol md="12">
                        <MDBTable>
                            <MDBTableHead color="primary-color" textWhite>
                                <tr>
                                    <th>#</th>
                                    <th>Policy id</th>
                                    <th>Description</th>
                                    <th>Select</th>
                                </tr>
                            </MDBTableHead>
                            <MDBTableBody>
                                {this.state.policies.map((policy, i) => {
                                        console.log(policy)
                                        return <tr key={i}>
                                            <td>{i}</td>
                                            <td>{policy.policy_id}</td>
                                            <td>{policy.description}</td>
                                            <td>
                                                <div
                                                    key={this.props.match.params.storename + "_" + i + "_" + policy.policy_id}
                                                    className="custom-control custom-checkbox">
                                                    <input onChange={this.onChange} type="checkbox"
                                                           name={this.props.match.params.storename + "_" + policy.policy_id}
                                                           className="custom-control-input"
                                                           id={this.props.match.params.storename + "_" + policy.policy_id}/>
                                                    <label className="custom-control-label"
                                                           htmlFor={this.props.match.params.storename + "_" + policy.policy_id}>Include</label>
                                                </div>
                                            </td>
                                        </tr>
                                    }
                                )}
                            </MDBTableBody>
                        </MDBTable>
                    </MDBCol>

                </MDBRow>

            </MDBContainer>
        );
    }
}

export default withRouter(ComposePolicies);
