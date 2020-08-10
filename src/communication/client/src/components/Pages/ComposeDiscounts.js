import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBRow, MDBTable, MDBTableBody, MDBTableHead} from "mdbreact";
import axios from "axios";
import {Redirect, withRouter} from "react-router-dom";
import {CREATED, OK} from "http-status-codes";

export class ComposeDiscounts extends Component {
    state = {
        discounts: [],
        redirectLink: null,
        msg: ""
    }
    selected = {}

    componentDidMount() {
        axios.get(
            "/fetch_discounts/" + this.props.getUserId() + "/" + this.props.match.params.storename
        )
            .then((res) => {
                this.setState({discounts: res.data !== null ? res.data.data : []});
            }).catch(error => {
            this.setState({msg: this.convertErrorToMessage(error.response.data["error"])})
            console.log(error)
        });
    }

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ")
            msg = msg.split("_").join(" ");
        }
        return msg;
    }

    onChange = (e) => {
        this.selected[e.target.id] = e.target.checked
    };

    combine = (by_op) => {
        let included_ids = Object.keys(this.selected).filter(key => this.selected[key]);
        axios.post(
            "/combine_discounts",
            {
                user_id: this.props.getUserId(),
                storename: this.props.match.params.storename,
                operator: by_op,
                discount_id_list: included_ids
            },
        )
            .then((res) => {
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
                                    <th>Discount id</th>
                                    <th>Description</th>
                                    <th>Select</th>
                                </tr>
                            </MDBTableHead>
                            <MDBTableBody>
                                {this.state.discounts.map((discount, i) => (
                                    <tr key={i}>
                                        <td>{i}</td>
                                        <td>{discount.discount_id}</td>
                                        <td>{discount.description}</td>
                                        <td>
                                            <div
                                                key={this.props.match.params.storename + "_" + i + "_" + discount.discount_id}
                                                className="custom-control custom-checkbox">
                                                <input onChange={this.onChange} type="checkbox"
                                                       name={discount.discount_id}
                                                       className="custom-control-input"
                                                       id={discount.discount_id}/>
                                                <label className="custom-control-label"
                                                       htmlFor={discount.discount_id}>Include</label>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </MDBTableBody>
                        </MDBTable>
                        <p onChange={this.onChange}
                           className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                    </MDBCol>

                </MDBRow>

            </MDBContainer>
        );
    }
}

export default withRouter(ComposeDiscounts);
